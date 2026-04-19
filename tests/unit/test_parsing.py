"""Tests for utils/parsing.py — syntactic string-to-Card parsing.

These tests verify ONLY the parsing logic, not any domain rules.
"""

import pytest

from tarot_engine.domain.cards import Card
from tarot_engine.domain.enums import Rank, Suit
from tarot_engine.utils.parsing import parse_card, parse_cards, parse_hand_string


class TestParseCard:
    # --- Trumps ---

    def test_parse_trump_single_digit(self) -> None:
        card = parse_card("T1")
        assert card == Card.trump(1)

    def test_parse_trump_double_digit(self) -> None:
        card = parse_card("T21")
        assert card == Card.trump(21)

    def test_parse_trump_mid_value(self) -> None:
        card = parse_card("T15")
        assert card == Card.trump(15)

    def test_parse_trump_case_insensitive(self) -> None:
        assert parse_card("t21") == Card.trump(21)

    def test_parse_trump_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_card("T0")
        with pytest.raises(ValueError):
            parse_card("T22")

    # --- Excuse ---

    def test_parse_excuse_full(self) -> None:
        assert parse_card("EXCUSE") == Card.excuse()

    def test_parse_excuse_exc(self) -> None:
        assert parse_card("EXC") == Card.excuse()

    def test_parse_excuse_single_e(self) -> None:
        assert parse_card("E") == Card.excuse()

    def test_parse_excuse_case_insensitive(self) -> None:
        assert parse_card("excuse") == Card.excuse()

    # --- Suited cards ---

    def test_parse_king_of_hearts(self) -> None:
        assert parse_card("KH") == Card.suited(Suit.HEARTS, Rank.ROI)

    def test_parse_ace_of_spades(self) -> None:
        assert parse_card("AS") == Card.suited(Suit.SPADES, Rank.AS)

    def test_parse_ten_of_diamonds(self) -> None:
        assert parse_card("10D") == Card.suited(Suit.DIAMONDS, Rank.TEN)

    def test_parse_queen_of_clubs(self) -> None:
        assert parse_card("QC") == Card.suited(Suit.CLUBS, Rank.DAME)

    def test_parse_dame_token(self) -> None:
        assert parse_card("DH") == Card.suited(Suit.HEARTS, Rank.DAME)

    def test_parse_valet_j_token(self) -> None:
        assert parse_card("JH") == Card.suited(Suit.HEARTS, Rank.VALET)

    def test_parse_valet_v_token(self) -> None:
        assert parse_card("VH") == Card.suited(Suit.HEARTS, Rank.VALET)

    def test_parse_cavalier(self) -> None:
        assert parse_card("CD") == Card.suited(Suit.DIAMONDS, Rank.CAVALIER)

    def test_parse_roi_r_token(self) -> None:
        assert parse_card("RH") == Card.suited(Suit.HEARTS, Rank.ROI)

    def test_parse_case_insensitive_suited(self) -> None:
        assert parse_card("kh") == Card.suited(Suit.HEARTS, Rank.ROI)

    def test_parse_with_whitespace(self) -> None:
        assert parse_card("  T21  ") == Card.trump(21)

    # --- Invalid inputs ---

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_card("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_card("   ")

    def test_gibberish_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_card("XYZ")

    def test_lone_suit_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_card("H")  # suit without rank

    def test_rank_without_suit_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_card("K")  # rank without suit


class TestParseCards:
    def test_parse_multiple_cards(self) -> None:
        cards = parse_cards(["T21", "KH", "EXCUSE"])
        assert cards == [Card.trump(21), Card.suited(Suit.HEARTS, Rank.ROI), Card.excuse()]

    def test_one_bad_token_raises_all_errors(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            parse_cards(["T21", "INVALID", "T1"])
        assert "INVALID" in str(exc_info.value) or "parse" in str(exc_info.value).lower()

    def test_empty_list_returns_empty(self) -> None:
        assert parse_cards([]) == []


class TestParseHandString:
    def test_comma_separated_string(self) -> None:
        result = parse_hand_string("T21,KH,EXCUSE")
        assert result == [Card.trump(21), Card.suited(Suit.HEARTS, Rank.ROI), Card.excuse()]

    def test_spaces_around_commas(self) -> None:
        result = parse_hand_string("T21 , KH , EXCUSE")
        assert len(result) == 3

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="[Ee]mpty"):
            parse_hand_string("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_hand_string("  ,  ,  ")

    def test_all_15_cards_from_string(self) -> None:
        from tarot_engine.domain.deck import generate_deck, HAND_SIZE
        deck = generate_deck()
        tokens = [str(c) for c in deck[:HAND_SIZE]]
        hand_str = ",".join(tokens)
        cards = parse_hand_string(hand_str)
        assert len(cards) == HAND_SIZE

    def test_integration_parse_then_build_hand(self) -> None:
        """Parsing then building a Hand must work end-to-end."""
        from tarot_engine.domain.deck import generate_deck, HAND_SIZE
        from tarot_engine.domain.hand import Hand

        deck = generate_deck()
        tokens = [str(c) for c in deck[:HAND_SIZE]]
        cards = parse_hand_string(",".join(tokens))
        hand = Hand.from_cards(cards)
        assert len(hand) == HAND_SIZE
