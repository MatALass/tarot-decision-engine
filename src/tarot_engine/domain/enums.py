"""Enumerated types for the Tarot domain.

All domain enums live here. No logic, no methods beyond standard enum helpers.
"""

from enum import Enum, auto


class Suit(Enum):
    """The four standard suits of a Tarot deck."""

    SPADES = "S"
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"


class Rank(Enum):
    """Ranks for suited cards, ordered by ascending point value.

    Tarot ranks: 1 (As) through 10, then Valet (J), Cavalier (C), Dame (Q), Roi (K).
    The integer value matches the display number for numeric cards.
    """

    AS = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    VALET = 11    # Jack
    CAVALIER = 12  # Knight (unique to Tarot — 14 cards per suit)
    DAME = 13     # Queen
    ROI = 14      # King


class Contract(Enum):
    """Playable contracts in ascending order of difficulty and multiplier.

    PASS is intentionally excluded: passing is a bidding *action*, not a contract.
    """

    PRISE = "PRISE"
    GARDE = "GARDE"
    GARDE_SANS = "GARDE_SANS"
    GARDE_CONTRE = "GARDE_CONTRE"

    def multiplier(self) -> int:
        """Score multiplier associated with each contract."""
        return {
            Contract.PRISE: 1,
            Contract.GARDE: 2,
            Contract.GARDE_SANS: 4,
            Contract.GARDE_CONTRE: 6,
        }[self]

    def uses_dog(self) -> bool:
        """Whether the taker is allowed to exchange with the dog (chien)."""
        return self in {Contract.PRISE, Contract.GARDE}

    def dog_counts_for_taker(self) -> bool:
        """Whether the dog cards count in the taker's tricks at scoring time."""
        return self in {Contract.PRISE, Contract.GARDE, Contract.GARDE_SANS}


class PlayerRole(Enum):
    """Role of a player within a deal."""

    TAKER = auto()    # Le preneur
    PARTNER = auto()  # Le partenaire appelé
    DEFENDER = auto() # Les défenseurs


class BidAction(Enum):
    """Actions available during the bidding phase.

    Separated from Contract because passing is not a contract.
    BidAction represents what a player *does* during the auction;
    Contract represents what is *played*.
    """

    PASS = "PASS"
    PRISE = "PRISE"
    GARDE = "GARDE"
    GARDE_SANS = "GARDE_SANS"
    GARDE_CONTRE = "GARDE_CONTRE"

    def is_contract(self) -> bool:
        """Return True if this bid action results in a playable contract."""
        return self != BidAction.PASS

    def to_contract(self) -> Contract:
        """Convert a non-pass bid action to its corresponding Contract.

        Raises ValueError if called on PASS.
        """
        if self == BidAction.PASS:
            raise ValueError("PASS cannot be converted to a Contract.")
        return Contract(self.value)
