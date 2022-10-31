# import logging
# from functools import wraps
# from typing import TYPE_CHECKING, Any, Callable, Optional
#
# if TYPE_CHECKING:
#     from blackJack.bj.models import GameSessionModel

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


#
#
# def get_point(card: str) -> int:
#     """
#     Возвращает ценность карты
#     :param card:
#     :return:
#     """
#     rang = card.split(" ")[1]
#     if rang == "A":
#         return 11
#     if rang.isdigit():
#         return int(rang)
#     return 10
#
#
# def check_session_game(logging_level=logging.ERROR) -> Any:
#     def func_wrapper(func: Callable):
#         @wraps(func)
#         async def inner(*args, **kwargs):
#             result: Optional["GameSessionModel"] = None
#             try:
#                 result = await func(*args, **kwargs)
#             except Exception as ex:
#                 msg = (
#                     f"db connection error...\n"
#                     f"location: before_execution,  {ex}\n"
#                     f"nested function: {func}\n"
#                 )
#                 logging.log(logging_level, msg)
#
#             return result
#
#         return inner
#
#     return func_wrapper
#
#
# def check_deck(deck: Deck, *args, **kwargs) -> bool:
#     """
#     Проверка колоды на наличие карт
#     :param deck:
#     :return:
#     """
#     return bool(len(deck))
#
#
# def check_cards(deck: Deck, count: int, *args, **kwargs) -> bool:
#     """
#     Проверка колоды на то что она может сдать запрашиваемое количество карт.
#     :param deck: колода.
#     :param count: количество карт
#     :return:
#     """
#     return len(deck) >= count
#
#
# def check(*args, **kwargs):
#     result = {}
#     for func in [check_deck, check_cards]:
#         result[func.__name__] = func(*args, **kwargs)
#     return result
