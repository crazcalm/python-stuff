import unittest
from unittest import TestCase

from python_stuff.playing_cards.cards import Card


class TestCard(TestCase):
    def test_init(self) -> None:
        card = Card(2, "suite")

        self.assertEqual(card.value, 2)
        self.assertEqual(card.suite, "suite")


if __name__ == "__main__":
    unittest.main()
