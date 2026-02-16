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

    @classmethod
    def four_suites(self) -> list[CardSuite]:
        return [
            self.SPADE,
            self.HEART,
            self.CLUB,
            self.DIAMOND,
        ]

    @classmethod
    def joker_suite(self) -> list[CardSuite]:
        return [self.JOKER]


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

    @classmethod
    def values_only_jokers(self) -> list[CardValue]:
        return [self.BIG_JOKER, self.SMALL_JOKER]

    @classmethod
    def values_no_jokers(self) -> list[CardValue]:
        exclude = [self.BIG_JOKER, self.SMALL_JOKER]

        return [
            getattr(self, item)
            for item in self._member_names_
            if getattr(self, item) not in exclude
        ]


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

    def __eq__(self, other) -> bool:
        return self.value == other.value and self.suite == other.suite


def create_cards(exclude: list[Card] | None = None) -> list[Card]:
    results = []

    joker_names = CardValue

    results = [
        Card(value, suite)
        for value in CardValue.values_no_jokers()
        for suite in CardSuite.four_suites()
    ]

    results += [
        Card(value, suite)
        for value in CardValue.values_only_jokers()
        for suite in CardSuite.joker_suite()
    ]

    # removing excluded cards
    if exclude:
        results = [card for card in results if card not in exclude]

    return results
