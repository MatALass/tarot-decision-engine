"""Hard inference constraints derived from observable Tarot play history."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import N_PLAYERS, generate_deck
from tarot_engine.domain.enums import Suit
from tarot_engine.domain.game_state import GameState
from tarot_engine.domain.rules import SuitLead, Trick, TrickCard, TrumpLead


@dataclass(frozen=True)
class HardConstraints:
    """Deterministic constraints inferred from public observations.

    The initial version intentionally stays conservative and only models hard
    impossibilities that are justified directly by the currently implemented
    rule engine:
    - cards already played cannot remain in any hand or in the dog
    - cards in the observed player's remaining hand cannot belong elsewhere
    - if a player fails to follow suit, they are void in that suit
    - if a player fails to cut when required, they have no trumps left
    - if a player undercuts, all higher trumps are impossible for that player
    """

    observed_player_index: int
    played_cards: frozenset[Card]
    observed_remaining_hand: frozenset[Card]
    void_suits_by_player: tuple[frozenset[Suit], ...]
    no_trumps_by_player: tuple[bool, ...]
    impossible_cards_by_player: tuple[frozenset[Card], ...]
    dog_impossible_cards: frozenset[Card]

    def __post_init__(self) -> None:
        if not (0 <= self.observed_player_index < N_PLAYERS):
            raise ValueError(
                f"observed_player_index must be in [0, {N_PLAYERS - 1}], got {self.observed_player_index}."
            )
        if len(self.void_suits_by_player) != N_PLAYERS:
            raise ValueError(
                f"void_suits_by_player must contain exactly {N_PLAYERS} entries, got {len(self.void_suits_by_player)}."
            )
        if len(self.no_trumps_by_player) != N_PLAYERS:
            raise ValueError(
                f"no_trumps_by_player must contain exactly {N_PLAYERS} entries, got {len(self.no_trumps_by_player)}."
            )
        if len(self.impossible_cards_by_player) != N_PLAYERS:
            raise ValueError(
                f"impossible_cards_by_player must contain exactly {N_PLAYERS} entries, got {len(self.impossible_cards_by_player)}."
            )


def derive_hard_constraints(game_state: GameState) -> HardConstraints:
    """Derive hard impossibility constraints from a GameState."""
    deck = generate_deck()
    observed_player_index = game_state.context.player_index
    observed_remaining_hand = frozenset(game_state.remaining_hand)
    played_cards = frozenset(game_state.played_cards)

    void_suits: list[set[Suit]] = [set() for _ in range(N_PLAYERS)]
    no_trumps = [False for _ in range(N_PLAYERS)]
    trump_upper_bounds: list[int] = [21 for _ in range(N_PLAYERS)]

    all_tricks = tuple(trick.cards for trick in game_state.completed_tricks.tricks) + _current_trick_as_partial(game_state.current_trick)
    for cards in all_tricks:
        _update_player_constraints_from_trick(cards, void_suits, no_trumps, trump_upper_bounds)

    impossible_cards_by_player: list[set[Card]] = [set() for _ in range(N_PLAYERS)]
    dog_impossible_cards = set(played_cards) | set(observed_remaining_hand)

    observed_exact_hand = set(deck) - set(observed_remaining_hand)
    impossible_cards_by_player[observed_player_index].update(observed_exact_hand)

    for player_index in range(N_PLAYERS):
        impossible_cards_by_player[player_index].update(played_cards)
        if player_index != observed_player_index:
            impossible_cards_by_player[player_index].update(observed_remaining_hand)

        for suit in void_suits[player_index]:
            impossible_cards_by_player[player_index].update(
                card for card in deck if card.suit == suit
            )
        if no_trumps[player_index]:
            impossible_cards_by_player[player_index].update(
                card for card in deck if card.is_trump
            )
        else:
            impossible_cards_by_player[player_index].update(
                card
                for card in deck
                if card.is_trump and card.trump_value > trump_upper_bounds[player_index]
            )

    return HardConstraints(
        observed_player_index=observed_player_index,
        played_cards=played_cards,
        observed_remaining_hand=observed_remaining_hand,
        void_suits_by_player=tuple(frozenset(values) for values in void_suits),
        no_trumps_by_player=tuple(no_trumps),
        impossible_cards_by_player=tuple(frozenset(values) for values in impossible_cards_by_player),
        dog_impossible_cards=frozenset(dog_impossible_cards),
    )


def _current_trick_as_partial(current_trick: tuple[TrickCard, ...]) -> tuple[tuple[TrickCard, ...], ...]:
    if not current_trick:
        return ()
    return (current_trick,)


def _update_player_constraints_from_trick(
    trick_cards: tuple[TrickCard, ...],
    void_suits: list[set[Suit]],
    no_trumps: list[bool],
    trump_upper_bounds: list[int],
) -> None:
    for idx, played in enumerate(trick_cards):
        prefix = trick_cards[:idx]
        if not prefix or played.card.is_excuse:
            continue
        trick_prefix = Trick(prefix)
        lead = trick_prefix.lead
        if isinstance(lead, SuitLead):
            _apply_suit_lead_constraints(
                played=played,
                led_suit=lead.suit,
                trick_prefix=trick_prefix,
                void_suits=void_suits,
                no_trumps=no_trumps,
                trump_upper_bounds=trump_upper_bounds,
            )
        elif isinstance(lead, TrumpLead):
            _apply_trump_lead_constraints(
                played=played,
                trick_prefix=trick_prefix,
                no_trumps=no_trumps,
                trump_upper_bounds=trump_upper_bounds,
            )


def _apply_suit_lead_constraints(
    *,
    played: TrickCard,
    led_suit: Suit,
    trick_prefix: Trick,
    void_suits: list[set[Suit]],
    no_trumps: list[bool],
    trump_upper_bounds: list[int],
) -> None:
    if played.card.suit == led_suit:
        return
    player_index = played.player_index
    void_suits[player_index].add(led_suit)
    if not played.card.is_trump:
        no_trumps[player_index] = True
        return
    _apply_trump_upper_bound(played, trick_prefix, trump_upper_bounds)


def _apply_trump_lead_constraints(
    *,
    played: TrickCard,
    trick_prefix: Trick,
    no_trumps: list[bool],
    trump_upper_bounds: list[int],
) -> None:
    if not played.card.is_trump:
        no_trumps[played.player_index] = True
        return
    _apply_trump_upper_bound(played, trick_prefix, trump_upper_bounds)


def _apply_trump_upper_bound(
    played: TrickCard,
    trick_prefix: Trick,
    trump_upper_bounds: list[int],
) -> None:
    highest = trick_prefix.highest_trump
    if highest is None:
        return
    if played.card.trump_value < highest.trump_value:
        current_bound = trump_upper_bounds[played.player_index]
        trump_upper_bounds[played.player_index] = min(current_bound, highest.trump_value)
