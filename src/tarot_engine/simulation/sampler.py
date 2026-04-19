"""Deal sampler: distribute unknown cards given a fixed player hand.

The contract is NOT a parameter: it does not affect card distribution.
Dog handling per contract is the responsibility of game_runner.

SIMPLIFICATIONS (MVP)
---------------------
King call heuristic:
  1. Prefer a king of a void suit not already in the taker's hand.
  2. Any king not in the taker's hand.
  3. If all four kings are in hand, call the first by suit order.

partner_index: 1-based index of the opponent holding the called king,
or None if the king landed in the dog.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from tarot_engine.domain.cards import Card
from tarot_engine.domain.deck import DOG_SIZE, HAND_SIZE, N_PLAYERS, generate_deck
from tarot_engine.domain.enums import Rank, Suit
from tarot_engine.domain.hand import Dog, Hand


@dataclass(frozen=True)
class SampledDeal:
    """A single sampled world: all hands + dog + called king."""
    hands: tuple[Hand, ...]
    dog: Dog
    called_king: Card
    partner_index: int | None


def sample_deal(taker_hand: Hand, rng: random.Random) -> SampledDeal:
    """Sample a plausible deal given the taker's known hand.

    Args:
        taker_hand: The observed player's 15-card hand (fixed).
        rng:        Seeded random instance for reproducibility.
    """
    deck = generate_deck()
    known = set(taker_hand.cards)
    unknown = [c for c in deck if c not in known]
    rng.shuffle(unknown)

    dog_cards = unknown[:DOG_SIZE]
    opponent_cards = unknown[DOG_SIZE:]

    opponent_hands: list[Hand] = []
    for i in range(N_PLAYERS - 1):
        start = i * HAND_SIZE
        opponent_hands.append(Hand.from_cards(opponent_cards[start: start + HAND_SIZE]))

    called_king = _choose_called_king(taker_hand)
    partner_index = _find_partner(called_king, opponent_hands)

    return SampledDeal(
        hands=(taker_hand,) + tuple(opponent_hands),
        dog=Dog.from_cards(dog_cards),
        called_king=called_king,
        partner_index=partner_index,
    )


def _choose_called_king(taker_hand: Hand) -> Card:
    taker_cards = set(taker_hand.cards)
    all_kings = [Card.suited(suit, Rank.ROI) for suit in Suit]
    kings_not_in_hand = [k for k in all_kings if k not in taker_cards]

    if not kings_not_in_hand:
        return all_kings[0]

    taker_suits = {c.suit for c in taker_hand.cards if c.suit is not None}
    void_suit_kings = [k for k in kings_not_in_hand if k.suit not in taker_suits]
    if void_suit_kings:
        return void_suit_kings[0]
    return kings_not_in_hand[0]


def _find_partner(called_king: Card, opponent_hands: list[Hand]) -> int | None:
    for i, hand in enumerate(opponent_hands):
        if called_king in hand:
            return i + 1
    return None
