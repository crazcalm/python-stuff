"""
Code related to Cards
"""

from enum import StrEnum


class CardSuite(StrEnum):
    """
    The 4 card suites plus an extra one for Jokers
    """

    SPADE = "spade"
    HEART = "heart"
    DIAMOND = "diamond"
    CLUB = "club"
    JOKER = "joker"


class CardValue(StrEnum):
    """
    The Values for standard cards
    """

    ACE = "ace"
    KING = "king"
    QUEEN = "queen"
    JACK = "jack"
    TEN = "ten"
    NINE = "nine"
    EIGHT = "eight"
    SEVEN = "seven"
    SIX = "six"
    FIVE = "five"
    FOUR = "four"
    THREE = "three"
    TWO = "two"
    BIG_JOKER = "big_joker"
    SMALL_JOKER = "small_joker"


class Card:
    """
    A Read only representation of a playing Card
    """

    def __init__(self, value: CardValue, suite: CardSuite) -> None:
        self._value = value
        self._suite = suite

    @property
    def value(self):
        return self._value

    @property
    def suite(self):
        return self._suite

    def __repr__(self) -> str:
        return f"Card({self.value.capitalize()}-{self.suite.capitalize()})"
