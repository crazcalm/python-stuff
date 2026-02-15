class Card:
    def __init__(self, value: int, suite: str) -> None:
        self._value = value
        self._suite = suite

    @property
    def value(self):
        return self._value

    @property
    def suite(self):
        return self._suite
