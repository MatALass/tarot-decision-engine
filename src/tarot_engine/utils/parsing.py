"""String-to-Card parser for CLI input.

Responsibility: syntactic parsing of user-supplied card strings into Card objects.
This module has NO domain logic — it does not validate hand sizes, check for
duplicates across a hand, or know anything about game rules.

Supported formats
-----------------
- Trumps:    "T1", "T21", "T15"   (T followed by 1–21)
- Excuse:    "EXCUSE", "EXC", "E"
- Suited:    "<RANK><SUIT>"

  Rank tokens (case-insensitive):
    A or AS    → AS
    2–10       → TWO … TEN
    J or V     → VALET (Valet)
    C          → CAVALIER (Cavalier / Knight)
    Q or D     → DAME (Queen)
    K or R     → ROI (King)

  Suit tokens (case-insensitive):
    S          → SPADES
    H          → HEARTS
    D          → DIAMONDS
    C          → CLUBS

  Examples: "KH" (King of Hearts), "AS" (Ace of Spades), "10D" (Ten of Diamonds)

Note on ambiguity:
  "C" alone is not a valid card string — it would collide between CLUBS and CAVALIER.
  "CD" → Cavalier of Diamonds, "CS" → Cavalier of Spades, etc.
"""

from __future__ import annotations

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Rank, Suit

# ---------------------------------------------------------------------------
# Token → Enum mappings
# ---------------------------------------------------------------------------

_RANK_TOKENS: dict[str, Rank] = {
    "A": Rank.AS,
    "AS": Rank.AS,
    "1": Rank.AS,
    "2": Rank.TWO,
    "3": Rank.THREE,
    "4": Rank.FOUR,
    "5": Rank.FIVE,
    "6": Rank.SIX,
    "7": Rank.SEVEN,
    "8": Rank.EIGHT,
    "9": Rank.NINE,
    "10": Rank.TEN,
    "J": Rank.VALET,
    "V": Rank.VALET,
    "C": Rank.CAVALIER,
    "Q": Rank.DAME,
    "D": Rank.DAME,
    "K": Rank.ROI,
    "R": Rank.ROI,
}

_SUIT_TOKENS: dict[str, Suit] = {
    "S": Suit.SPADES,
    "H": Suit.HEARTS,
    "D": Suit.DIAMONDS,
    "C": Suit.CLUBS,
}

_EXCUSE_TOKENS: frozenset[str] = frozenset({"EXCUSE", "EXC", "E"})


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_card(token: str) -> Card:
    """Parse a single card token string into a Card object.

    Args:
        token: A non-empty string representing one card (e.g. "T21", "KH", "EXCUSE").

    Returns:
        The corresponding Card instance.

    Raises:
        ValueError: If the token cannot be parsed into a valid Card.
    """
    normalised = token.strip().upper()
    if not normalised:
        raise ValueError("Card token must not be empty.")

    # --- Excuse ---
    if normalised in _EXCUSE_TOKENS:
        return Card.excuse()

    # --- Trump: starts with T followed by digits ---
    if normalised.startswith("T") and normalised[1:].isdigit():
        value = int(normalised[1:])
        try:
            return Card.trump(value)
        except ValueError:
            raise ValueError(
                f"Invalid trump value in '{token}': must be between 1 and 21."
            )

    # --- Suited card: try to split into rank + suit ---
    return _parse_suited(token, normalised)


def parse_cards(tokens: list[str]) -> list[Card]:
    """Parse a list of card token strings into a list of Card objects.

    Args:
        tokens: List of card string tokens.

    Returns:
        List of Card instances in the same order as the input.

    Raises:
        ValueError: If any token cannot be parsed.
    """
    cards = []
    errors = []
    for token in tokens:
        try:
            cards.append(parse_card(token))
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        raise ValueError(
            f"Failed to parse {len(errors)} card(s):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
    return cards


def parse_hand_string(hand_str: str) -> list[Card]:
    """Parse a comma-separated hand string into a list of Card objects.

    Args:
        hand_str: Comma-separated card tokens, e.g. "T21,KH,QD,EXCUSE".

    Returns:
        List of Card instances.

    Raises:
        ValueError: If any token is invalid.
    """
    tokens = [t.strip() for t in hand_str.split(",") if t.strip()]
    if not tokens:
        raise ValueError("Hand string is empty or contains only whitespace.")
    return parse_cards(tokens)


def parse_trick_card(token: str):
    """Parse one trick-entry token formatted as '<player_index>:<card>'."""
    normalised = token.strip()
    if not normalised:
        raise ValueError("Trick-card token must not be empty.")
    if ":" not in normalised:
        raise ValueError(
            f"Cannot parse trick-card token '{token}'. Expected format '<player_index>:<card>'."
        )
    player_raw, card_raw = normalised.split(":", 1)
    try:
        player_index = int(player_raw.strip())
    except ValueError as exc:
        raise ValueError(
            f"Invalid player index in trick-card token '{token}': '{player_raw.strip()}'."
        ) from exc
    if not (0 <= player_index <= 4):
        raise ValueError(
            f"player_index must be in [0, 4] in trick-card token '{token}', got {player_index}."
        )
    from tarot_engine.domain.rules import TrickCard

    return TrickCard(card=parse_card(card_raw.strip()), player_index=player_index)


def parse_trick_string(trick_str: str):
    """Parse a '|' separated trick string into ordered TrickCard entries.

    Example:
        '0:T21|1:KH|2:QH'
    """
    if not trick_str.strip():
        return ()
    tokens = [token.strip() for token in trick_str.split("|") if token.strip()]
    return tuple(parse_trick_card(token) for token in tokens)


def format_card_token(card: Card) -> str:
    """Return a canonical parseable token for a Card."""
    if card.is_excuse:
        return "EXCUSE"
    if card.is_trump:
        return f"T{card.trump_value}"
    assert card.suit is not None and card.rank is not None
    suit_token = {
        Suit.SPADES: "S",
        Suit.HEARTS: "H",
        Suit.DIAMONDS: "D",
        Suit.CLUBS: "C",
    }[card.suit]
    rank_token = {
        Rank.AS: "AS",
        Rank.TWO: "2",
        Rank.THREE: "3",
        Rank.FOUR: "4",
        Rank.FIVE: "5",
        Rank.SIX: "6",
        Rank.SEVEN: "7",
        Rank.EIGHT: "8",
        Rank.NINE: "9",
        Rank.TEN: "10",
        Rank.VALET: "J",
        Rank.CAVALIER: "C",
        Rank.DAME: "Q",
        Rank.ROI: "K",
    }[card.rank]
    return f"{rank_token}{suit_token}"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_suited(original: str, normalised: str) -> Card:
    """Attempt to parse a suited card from a normalised token.

    Strategy: try rank tokens of length 2 first (e.g. "10", "AS"), then length 1.
    The last character is always attempted as the suit token.

    Raises:
        ValueError: If parsing fails.
    """
    # Try 2-char rank prefix first (handles "10H", "ASH" etc.)
    for rank_len in (2, 1):
        if len(normalised) < rank_len + 1:
            continue
        rank_token = normalised[:rank_len]
        suit_token = normalised[rank_len:]

        if rank_token in _RANK_TOKENS and suit_token in _SUIT_TOKENS:
            return Card.suited(
                suit=_SUIT_TOKENS[suit_token],
                rank=_RANK_TOKENS[rank_token],
            )

    raise ValueError(
        f"Cannot parse '{original}' as a card. "
        f"Expected formats: 'T<n>' for trumps (1–21), "
        f"'EXCUSE'/'EXC'/'E' for the Excuse, "
        f"or '<RANK><SUIT>' for suited cards (e.g. 'KH', '10D', 'AS')."
    )
