import random

Card = str
Deck = list[Card]
SUITS: list[str] = "♠ ♡ ♢ ♣".split()
RANKS: list[str] = "2 3 4 5 6 7 8 9 10 J Q K A".split()


def create_deck(count_deck: int) -> Deck:
    """
    Создать колоду, из count_deck колод
    :param count_deck:  количество колод
    :return:
    """
    deck = [
        suit + " " + rang for _ in range(count_deck) for rang in RANKS for suit in SUITS
    ]
    random.shuffle(deck)
    return deck
