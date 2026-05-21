"""Turn-by-turn runner built on WorldState/GameState transitions."""

from __future__ import annotations

from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Contract
from tarot_engine.domain.game_state import GameState, InitialDealContext, WorldState
from tarot_engine.domain.hand import Hand
from tarot_engine.domain.observations import CardPlayedObservation, TrickCompletedObservation
from tarot_engine.domain.projections import build_all_game_states
from tarot_engine.domain.transitions import Observation, apply_play_action_world
from tarot_engine.domain.trick import TrickHistory
from tarot_engine.domain.scoring import DealResult, score_deal
from tarot_engine.simulation.game_runner import _select_discards, _taker_camp
from tarot_engine.simulation.sampler import SampledDeal
from tarot_engine.simulation.turn_policies import HeuristicTurnPolicy, TurnPolicy


@dataclass(frozen=True)
class TurnByTurnRunResult:
    """Result of a full turn-by-turn simulated play-out."""

    final_world_state: WorldState
    observations: tuple[Observation, ...]
    winner_piles_by_player: tuple[tuple[Card, ...], ...]
    score: DealResult



def build_initial_world_state(
    deal: SampledDeal,
    contract: Contract,
    *,
    observed_player_index: int = 0,
) -> tuple[WorldState, tuple[tuple[Card, ...], ...]]:
    """Build the initial WorldState and initial scoring piles.

    Returns:
        world_state, initial_winner_piles_by_player
    """
    remaining_hands = [tuple(hand.cards) for hand in deal.hands]
    winner_piles: list[list[Card]] = [[] for _ in range(len(remaining_hands))]

    dog_zone = tuple(deal.dog.cards)
    taker_index = 0
    if contract.uses_dog():
        taker_cards = list(remaining_hands[taker_index]) + list(dog_zone)
        discards = _select_discards(taker_cards, n=3)
        for card in discards:
            taker_cards.remove(card)
        remaining_hands[taker_index] = tuple(taker_cards)
        winner_piles[taker_index].extend(discards)
        dog_zone = tuple(discards)

    observed_hand = Hand.from_cards(list(_reconstruct_observed_initial_hand(remaining_hands, observed_player_index)))
    context = InitialDealContext(
        player_index=observed_player_index,
        taker_index=taker_index,
        contract=contract,
        initial_hand=observed_hand,
        partner_index=deal.partner_index,
    )
    game_state = GameState(
        context=context,
        remaining_hand=remaining_hands[observed_player_index],
        current_trick=(),
        completed_tricks=TrickHistory(tricks=()),
        next_player_index=taker_index,
    )
    world_state = WorldState(
        game_state=game_state,
        remaining_hands_by_player=tuple(remaining_hands),
        dog=dog_zone,
    )
    return world_state, tuple(tuple(pile) for pile in winner_piles)



def run_sampled_deal_turn_by_turn(
    deal: SampledDeal,
    contract: Contract,
    *,
    policies_by_player: tuple[TurnPolicy, ...] | None = None,
    observed_player_index: int = 0,
) -> TurnByTurnRunResult:
    """Play a full sampled deal using turn-by-turn states and policies."""
    if policies_by_player is None:
        policies_by_player = tuple(HeuristicTurnPolicy() for _ in range(len(deal.hands)))
    if len(policies_by_player) != len(deal.hands):
        raise ValueError(
            f"policies_by_player must contain exactly {len(deal.hands)} policies, got {len(policies_by_player)}."
        )

    world_state, initial_piles = build_initial_world_state(
        deal,
        contract,
        observed_player_index=observed_player_index,
    )
    winner_piles = [list(pile) for pile in initial_piles]
    all_observations: list[Observation] = []

    while not is_terminal_world_state(world_state):
        projected_states = build_all_game_states(world_state)
        acting_player = world_state.game_state.next_player_index
        action = policies_by_player[acting_player].select_action(projected_states[acting_player])
        world_state, observations = apply_play_action_world(world_state, action)
        all_observations.extend(observations)
        _update_winner_piles_from_observations(winner_piles, observations)

    score = _score_turn_run(
        winner_piles=winner_piles,
        contract=contract,
        partner_index=deal.partner_index,
        dog_cards=tuple(deal.dog.cards),
    )
    return TurnByTurnRunResult(
        final_world_state=world_state,
        observations=tuple(all_observations),
        winner_piles_by_player=tuple(tuple(pile) for pile in winner_piles),
        score=score,
    )



def is_terminal_world_state(world_state: WorldState) -> bool:
    """Return True when all players have exhausted their hands and no trick is open."""
    return (
        not world_state.game_state.current_trick
        and all(len(hand) == 0 for hand in world_state.remaining_hands_by_player)
    )



def _update_winner_piles_from_observations(
    winner_piles: list[list[Card]], observations: tuple[Observation, ...]
) -> None:
    for observation in observations:
        if isinstance(observation, CardPlayedObservation):
            continue
        if isinstance(observation, TrickCompletedObservation):
            winner_piles[observation.trick.winner_index].extend(observation.trick.played_cards)
            continue
        raise TypeError(f"Unsupported observation type: {type(observation)!r}")



def _score_turn_run(
    *,
    winner_piles: list[list[Card]],
    contract: Contract,
    partner_index: int | None,
    dog_cards: tuple[Card, ...],
) -> DealResult:
    taker_camp = _taker_camp(0, partner_index)
    taker_pile = [card for player_index in taker_camp for card in winner_piles[player_index]]
    if contract == Contract.GARDE_SANS:
        taker_pile.extend(dog_cards)
    taker_points = sum(card.point_value for card in taker_pile)
    bout_count = sum(1 for card in taker_pile if card.is_bout)
    return score_deal(taker_points, bout_count, contract)



def _reconstruct_observed_initial_hand(
    remaining_hands: list[tuple[Card, ...]], observed_player_index: int
) -> tuple[Card, ...]:
    return tuple(remaining_hands[observed_player_index])
