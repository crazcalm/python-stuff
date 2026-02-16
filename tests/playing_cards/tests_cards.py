import unittest
from unittest import TestCase

from python_stuff.playing_cards.cards import (
    Card,
    CardValue,
    CardSuite,
)


class TestCard(TestCase):
    def setUp(self):
        card_value = CardValue.TWO
        card_suite = CardSuite.SPADE

        self.card = Card(card_value, card_suite)

    def test_init(self) -> None:
        self.assertEqual(self.card.value, CardValue.TWO)
        self.assertEqual(self.card.suite, CardSuite.SPADE)

    def test__repr__(self) -> None:
        expected = "Card(Two-Spade)"
        result = str(self.card)

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
