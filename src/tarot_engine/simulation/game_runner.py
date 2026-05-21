"""Game runner: execute a complete simulated deal.

SIMPLIFICATIONS (MVP)
---------------------
Dog exchange (PRISE/GARDE): taker receives dog, discards exactly 3 non-bout
  cards (low suited first, then low trumps, then kings). Discards count in
  taker's scoring pile.

GARDE_SANS: dog set aside, counts for taker at scoring.
GARDE_CONTRE: dog set aside, counts for defenders.

Partner: identified by who holds the called king. If king is in dog,
  taker plays alone (taker's camp = {taker only}).

Excuse (MVP simplification): Excuse never wins; its points go to the
  player who played it (added to that player's pile). Standard end-game
  Excuse swap is not implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import HAND_SIZE, N_PLAYERS
from tarot_engine.domain.enums import Contract, Rank
from tarot_engine.domain.rules import Trick, TrickCard, legal_cards, trick_winner
from tarot_engine.domain.scoring import DealResult, score_deal
from tarot_engine.simulation.policies import choose_card
from tarot_engine.simulation.sampler import SampledDeal

_DISCARD_COUNT = 3


@dataclass
class _PlayerState:
    index: int
    hand: list[Card]
    won_cards: list[Card] = field(default_factory=list)


def run_deal(deal: SampledDeal, contract: Contract) -> DealResult:
    """Simulate a complete deal and return the scored result."""
    taker_index = 0
    players = [
        _PlayerState(index=i, hand=list(deal.hands[i].cards))
        for i in range(N_PLAYERS)
    ]
    dog_cards = list(deal.dog.cards)

    if contract.uses_dog():
        _apply_dog_exchange(players[taker_index], dog_cards)
        dog_for_taker = False
    elif contract.dog_counts_for_taker():
        dog_for_taker = True
    else:
        dog_for_taker = False

    current_leader = taker_index
    for _ in range(HAND_SIZE):
        current_leader = _play_trick(players, current_leader, taker_index)

    taker_camp = _taker_camp(taker_index, deal.partner_index)
    taker_pile = _collect_camp_cards(players, taker_camp)
    if dog_for_taker:
        taker_pile.extend(dog_cards)

    taker_points = sum(c.point_value for c in taker_pile)
    bout_count = sum(1 for c in taker_pile if c.is_bout)
    return score_deal(taker_points, bout_count, contract)


def _play_trick(
    players: list[_PlayerState],
    leader_index: int,
    taker_index: int,
) -> int:
    trick_cards: list[TrickCard] = []
    trick = Trick(cards_played=())
    for offset in range(N_PLAYERS):
        player_index = (leader_index + offset) % N_PLAYERS
        player = players[player_index]
        hand_tuple = tuple(player.hand)
        legal = legal_cards(hand_tuple, trick)
        chosen = choose_card(player_index, legal, trick, taker_index)
        player.hand.remove(chosen)
        trick_cards.append(TrickCard(card=chosen, player_index=player_index))
        trick = Trick(cards_played=tuple(trick_cards))
    winner_index = trick_winner(trick)
    players[winner_index].won_cards.extend(tc.card for tc in trick.cards_played)
    return winner_index


def _apply_dog_exchange(taker: _PlayerState, dog_cards: list[Card]) -> None:
    """Give taker the dog, then discard exactly 3 non-bout cards."""
    taker.hand.extend(dog_cards)
    discards = _select_discards(taker.hand, n=_DISCARD_COUNT)
    if len(discards) != _DISCARD_COUNT:
        raise ValueError(
            f"_select_discards must return exactly {_DISCARD_COUNT} cards, "
            f"got {len(discards)}."
        )
    for card in discards:
        taker.hand.remove(card)
    taker.won_cards.extend(discards)


def _select_discards(hand: list[Card], n: int) -> list[Card]:
    """Select n cards to discard, never selecting bouts or the Excuse."""
    candidates: list[Card] = []
    tier1 = sorted(
        [c for c in hand if c.suit is not None and not c.is_bout and c.rank != Rank.ROI],
        key=lambda c: c.rank.value if c.rank else 0,
    )
    candidates.extend(tier1)
    if len(candidates) >= n:
        return candidates[:n]
    tier2 = sorted(
        [c for c in hand if c.is_trump and not c.is_bout],
        key=lambda c: c.trump_value,
    )
    candidates.extend(tier2)
    if len(candidates) >= n:
        return candidates[:n]
    tier3 = [c for c in hand if c.rank == Rank.ROI]
    candidates.extend(tier3)
    if len(candidates) >= n:
        return candidates[:n]
    raise ValueError(
        f"Cannot select {n} non-bout discards from a {len(hand)}-card hand."
    )


def _taker_camp(taker_index: int, partner_index: int | None) -> frozenset[int]:
    if partner_index is None:
        return frozenset({taker_index})
    return frozenset({taker_index, partner_index})


def _collect_camp_cards(
    players: list[_PlayerState],
    camp: frozenset[int],
) -> list[Card]:
    pile: list[Card] = []
    for player in players:
        if player.index in camp:
            pile.extend(player.won_cards)
    return pile
