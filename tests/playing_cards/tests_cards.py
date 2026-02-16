import unittest
from unittest import TestCase

from python_stuff.playing_cards.cards import (
    Card,
    CardValue,
    CardSuite,
    create_cards,
)


class TestCardValue(TestCase):
    def test_values_only_jokers(self) -> None:
        expected_count = 2
        results = CardValue.values_only_jokers()

        self.assertIn(CardValue.BIG_JOKER, results)
        self.assertIn(CardValue.SMALL_JOKER, results)
        self.assertEqual(len(results), expected_count)

    def test_values_no_jokers(self) -> None:
        expected_count = 13
        results = CardValue.values_no_jokers()

        self.assertNotIn(CardValue.BIG_JOKER, results)
        self.assertNotIn(CardValue.SMALL_JOKER, results)
        self.assertEqual(len(results), expected_count)


class TestCardSuite(TestCase):
    def test_joker_suite(self) -> None:
        expected = [CardSuite.JOKER]
        result = CardSuite.joker_suite()
        self.assertListEqual(result, expected)

    def test_four_suites(self) -> None:
        expected_count = 4
        results = CardSuite.four_suites()

        self.assertNotIn(CardSuite.JOKER, results)
        self.assertEqual(len(results), expected_count)


class TestCreateCards(TestCase):
    def test_excluding_cards(self) -> None:
        expected_count = 52
        exclude_list = [
            Card(CardValue.ACE, CardSuite.SPADE),
            Card(CardValue.BIG_JOKER, CardSuite.JOKER),
        ]

        results = create_cards(exclude=exclude_list)

        for card in exclude_list:
            self.assertNotIn(card, results)
        self.assertEqual(len(results), expected_count)

    def test_all_cards(self) -> None:
        expected_count = 54
        results = create_cards()

        self.assertEqual(len(results), expected_count)


class TestCard(TestCase):
    def setUp(self) -> None:
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

    def test__eq__(self) -> None:
        new_card = Card(self.card.value, self.card.suite)

        self.assertEqual(new_card, self.card)


if __name__ == "__main__":
    unittest.main()
