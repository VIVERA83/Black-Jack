from typing import Callable, Optional

from base.base_accessor import BaseAccessor
from bj.models import GameSessionModel, StatusGameEnum, StatusPlayerEnum
from bj.schemes import Content, GamePlay


class BJGamePlay(BaseAccessor):
    game_session: Optional[GameSessionModel] = None

    async def gameplay(self, gameplay: GamePlay) -> GameSessionModel:
        """Основной метод, выполняет поступившею команду"""
        if gameplay.action == "new game":
            await self.create_new_game(gameplay.content)
        else:
            await self.create_game_session(gameplay.game_session_id)

            if (
                self.game_session
                and gameplay.action in self.game_session.allowed_actions
                or (gameplay.action is None and not self.game_session.allowed_actions)
            ):
                match gameplay.action:
                    case "new round":
                        self.create_new_round()
                    case "move bot":
                        self.move_bot()
                    case "move player":
                        self.move_player()
                    case "pass":
                        self.skipping_move()
                    case "round end":
                        self.round_end()
                    case "game end":
                        self.game_end()
            elif not self.game_session:
                raise ValueError("Game session not found")
            else:
                raise ValueError(
                    f"The game session is waiting for one of the commands: {self.game_session.allowed_actions}"
                )
        self.check_allowed_actions()
        if not self.game_session.allowed_actions:
            self.get_next_player()

        await self.update_game_session()

        return self.game_session

    async def update_game_session(self):
        await self.app.store.bj.bulk_update_player(self.game_session.players)
        self.game_session = await self.app.store.bj.update_game_session(
            self.game_session
        )

    async def create_new_game(self, content: Content):
        self.game_session = await self.app.store.bj.create_game_session(**content.dict)
        self.game_session.allowed_actions = ["new round"]

    async def create_game_session(self, game_session_id: int):
        self.game_session = await self.app.store.bj.get_game_session_by_id(
            game_session_id
        )

    def calculate_points(self):
        bot = self.game_session.players[self.get_bot_index()]
        for player in self.game_session.players:
            if player.user_id != bot.user_id:
                score = 2 if player.score == 21 else 0
                if (bot.score < player.score < 22) or (player.score < 22 < bot.score):
                    score += 2
                else:
                    score -= 2
                player.balance += score

    def clear_scores(self):
        for player in self.game_session.players:
            player.score = 0

    def clear_hands(self):
        [player.hand.clear() for player in self.game_session.players]

    def create_new_round(self, count_cards: int = 2):
        first_index = -1
        self.clear_scores()
        self.clear_hands()
        for index, user_vk_id in enumerate(self.game_session.players_list):
            for player in self.game_session.players:
                if (player.user_id == user_vk_id) and (
                    player.status == StatusPlayerEnum.active
                ):
                    cards = [self.game_session.deck.pop() for _ in range(count_cards)]
                    player.hand.extend(cards)
                    for card in cards:
                        player.score += get_point(card, player.score)
                    if first_index < 0:
                        first_index = index
                        self.game_session.index = index
                        self.game_session.current_user_vk_id = user_vk_id
                        self.game_session.allowed_actions = ["move player", "pass"]

    def round_end(self):
        self.calculate_points()
        self.clear_scores()
        self.clear_hands()
        self.game_session.index = 0
        self.game_session.allowed_actions = ["new round", "game end"]

    def move_bot(self):
        index = self.get_index()
        if self.game_session.players[index].score < 17:
            self.move_player()
        if self.game_session.players[index].score >= 17:
            self.game_session.index += 1
        self.game_session.allowed_actions = ["move bot", "round end"]

    def move_player(self):
        index = self.get_index()
        self.game_session.players[index].hand.append(self.game_session.deck.pop())
        self.game_session.players[index].score += get_point(
            self.game_session.players[index].hand[-1],
            self.game_session.players[index].score,
        )
        self.game_session.allowed_actions = [
            "move player",
            "pass",
            "move bot",
            "round end",
        ]

    def skipping_move(self):
        self.get_next_player()
        self.game_session.allowed_actions = ["move player", "pass", "move bot"]

    def get_index(self):
        for index, player in enumerate(self.game_session.players):
            if self.game_session.current_user_vk_id == player.user_id:
                return index

    def get_bot_index(self):
        for index, player in enumerate(self.game_session.players):
            if player.user_id == 0:
                return index

    def game_end(self):
        self.game_session.status_game = StatusGameEnum.finished

    def get_check_list(self) -> dict[str, list[Callable]]:
        return {
            "new round": [
                self.check_deck,
                self.check_players,
                self.check_new_round,
                self.check_active_game,
            ],
            "move player": [
                self.check_card,
                self.check_player_score,
                self.check_active_game,
                self.check_not_bot,
            ],
            "pass": [
                self.check_player_score,
                self.check_active_game,
                self.check_not_bot,
            ],
            "game end": [self.check_game_end],
            "move bot": [
                self.check_card,
                self.check_bot_score,
                self.check_active_game,
                self.check_bot,
            ],
            "round end": [self.check_round_end],
        }

    def check_allowed_actions(self):

        check_list = self.get_check_list()
        action_list = []

        for action in self.game_session.allowed_actions:

            if all([check() for check in check_list.get(action)]):
                action_list.append(action)
        self.game_session.allowed_actions = action_list

    def check_round_end(self):
        return self.game_session.index == len(self.game_session.players_list)

    def check_not_bot(self):
        return self.game_session.current_user_vk_id != 0

    def check_bot(self):
        return self.game_session.current_user_vk_id == 0

    def check_active_game(self):
        return self.game_session.status_game == StatusGameEnum.active

    def check_new_round(self) -> bool:
        """
        Проверка на то что возможно начать новый раунд, нужно что бы был окончен текущий раунд.
        """
        return self.game_session.index == 0

    def check_game_end(self):
        return not self.check_deck() or not self.check_card()

    def check_player_score(self):
        """
        Проверка очков у игрока.
        """
        if self.game_session.index >= len(self.game_session.players_list):
            return False
        return self.game_session.players[self.game_session.index].score < 21

    def check_bot_score(self):
        """
        Проверка очков у игрока.
        """
        return self.game_session.players[self.get_bot_index()].score < 17

    def check_card(self):
        """Проверка колоды на наличие карты"""
        return bool(len(self.game_session.deck))

    def check_deck(self):
        """Проверка колоды на наличие в ней нужного количества карт для раздачи нового раунда"""
        return len(self.game_session.players_list) * 2 <= len(self.game_session.deck)

    def check_players(self):
        """Проверка на то что есть активные игроки"""
        count = -1
        for player in self.game_session.players:
            if player.status == StatusPlayerEnum.active:
                count += 1
        return bool(count)

    def get_next_player(self):
        for index in range(
            self.game_session.index + 1, len(self.game_session.players_list)
        ):
            for player in self.game_session.players:
                if (
                    player.user_id == self.game_session.players_list[index]
                    and player.status == StatusPlayerEnum.active
                    and player.score < 21
                ):
                    self.game_session.index = index
                    self.game_session.current_user_vk_id = player.user_id
                    self.game_session.allowed_actions = [
                        "move player",
                        "pass",
                        "move bot",
                        "game end",
                        "new round",
                        "round end",
                    ]
                    self.check_allowed_actions()

        self.game_session.index += 1
        self.game_session.allowed_actions = ["round end"]


def get_point(card: str, scores: int) -> int:
    """
    # ПЕРЕДЕЛАТЬ
    Возвращает ценность карты, учетом Туза
    :param card:
    :param scores:
    :return:
    """
    rang = card.split(" ")[1]
    if rang == "A":
        return 11 if (scores + 11) <= 21 else 1
    if rang.isdigit():
        return int(rang)
    return 10
