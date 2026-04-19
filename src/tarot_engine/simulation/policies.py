"""Play policies: heuristics that decide which card to play.

SINGLE POLICY FOR ALL PLAYERS (MVP)
-------------------------------------
Role-differentiated strategies are deferred to a later step.

HEURISTIC LOGIC
---------------
Leading:
  Taker:   highest trump to draw opponent trumps; else highest suited card.
  Others:  lowest card to preserve strong cards.

Following:
  Taker:   highest winning card if possible; else lowest card.
  Others:  lowest winning card if possible; else lowest card.

"Wins" means the card beats the current trick winner per trump-over-suit
priority. The policy is fully deterministic given the same inputs.

LOWEST CARD priority (when conceding):
  Tier 1: lowest-rank suited non-bout non-king.
  Tier 2: lowest non-bout trump.
  Tier 3: kings.
  Tier 4: bouts.
  Last resort: Excuse.
"""

from __future__ import annotations

from tarot_engine.domain.cards import Card
from tarot_engine.domain.rules import SuitLead, Trick, TrickCard


def choose_card(
    player_index: int,
    legal: tuple[Card, ...],
    trick: Trick,
    taker_index: int,
) -> Card:
    """Choose a card to play using the MVP heuristic policy."""
    assert legal, "legal must be non-empty"
    is_taker = player_index == taker_index
    is_leading = trick.is_empty or trick.lead is None
    if is_leading:
        return _choose_lead(legal, is_taker)
    return _choose_follow(legal, trick, is_taker)


def _choose_lead(legal: tuple[Card, ...], is_taker: bool) -> Card:
    if is_taker:
        trumps = [c for c in legal if c.is_trump]
        if trumps:
            return max(trumps, key=lambda c: c.trump_value)
        non_excuse = [c for c in legal if not c.is_excuse]
        if non_excuse:
            return max(non_excuse, key=lambda c: c.rank.value if c.rank else 0)
        return legal[0]
    else:
        non_excuse = [c for c in legal if not c.is_excuse]
        return _lowest_card(non_excuse) if non_excuse else legal[0]


def _choose_follow(legal: tuple[Card, ...], trick: Trick, is_taker: bool) -> Card:
    current_winner = trick.current_winner
    winning = [
        c for c in legal
        if not c.is_excuse
        and current_winner is not None
        and _beats(c, current_winner.card, trick)
    ]
    if winning:
        return _highest_card(winning) if is_taker else _lowest_winner(winning)
    return _lowest_card(list(legal))


def _beats(candidate: Card, current_best: Card, trick: Trick) -> bool:
    if candidate.is_excuse:
        return False
    if current_best.is_trump:
        return candidate.is_trump and candidate.trump_value > current_best.trump_value
    if candidate.is_trump:
        return True
    lead = trick.lead
    if isinstance(lead, SuitLead) and candidate.suit == lead.suit:
        assert candidate.rank is not None and current_best.rank is not None
        return candidate.rank.value > current_best.rank.value
    return False


def _highest_card(cards: list[Card]) -> Card:
    trumps = [c for c in cards if c.is_trump]
    if trumps:
        return max(trumps, key=lambda c: c.trump_value)
    suited = [c for c in cards if not c.is_excuse]
    if suited:
        return max(suited, key=lambda c: c.rank.value if c.rank else 0)
    return cards[0]


def _lowest_winner(winning: list[Card]) -> Card:
    suited = [c for c in winning if c.suit is not None]
    if suited:
        return min(suited, key=lambda c: c.rank.value if c.rank else 0)
    return min(winning, key=lambda c: c.trump_value if c.is_trump else 0)


def _lowest_card(cards: list[Card]) -> Card:
    from tarot_engine.domain.enums import Rank
    tier1 = [c for c in cards if c.suit is not None and not c.is_bout and c.rank != Rank.ROI]
    if tier1:
        return min(tier1, key=lambda c: c.rank.value)  # type: ignore[union-attr]
    tier2 = [c for c in cards if c.is_trump and not c.is_bout]
    if tier2:
        return min(tier2, key=lambda c: c.trump_value)
    tier3 = [c for c in cards if c.rank is not None]
    from tarot_engine.domain.enums import Rank as R
    tier3k = [c for c in tier3 if c.rank == R.ROI]
    if tier3k:
        return tier3k[0]
    tier4 = [c for c in cards if c.is_bout and not c.is_excuse]
    if tier4:
        return min(tier4, key=lambda c: c.trump_value if c.is_trump else 0)
    return cards[0]
