from typing import Optional

from base.base_accessor import BaseAccessor
from bj.models import GameSessionModel, PlayerModel
from bj.schemes import Content


class BJGamePlay(BaseAccessor):
    game_session: Optional[GameSessionModel] = None
    index: int = None

    async def new_game(self, content: Content) -> GameSessionModel:
        return await self.app.store.bj.create_game_session(**content.dict)

    async def new_round(self, game_session_id: int) -> GameSessionModel:
        await self._get_game_session(game_session_id)
        if not self._check_game_end():
            self._clear_scores()
            self._clear_hands()
            self._deal_cards(2)
            self.index = 0
            self.game_session.current_user_vk_id = self.game_session.players[0].user_id
            self.game_session.allowed_actions = ["move player"]
        return await self.update_game_session()

    async def move_player(
        self, game_session_id: int, player_id: int, action: str
    ) -> GameSessionModel:
        await self._get_game_session(game_session_id)
        self._check_turn_player(player_id)
        if (
            action == "move player"
            and self._check_deal_card()
            and self.game_session.deck
        ):
            card = self.game_session.deck.pop()
            score = self._get_point(card, self.game_session.players[self.index].score)
            self.game_session.players[self.index].hand.append(card)
            self.game_session.players[self.index].score += score
            if self._check_deal_card():
                self.index -= 1
        self.index += 1
        self._check_round()
        return await self.update_game_session()

    async def quit_game_player(
        self, game_session_id: int, player_id: int
    ) -> GameSessionModel:
        await self._get_game_session(game_session_id)
        for index, player in enumerate(self.game_session.players):
            if player.user_id == player_id:
                if index < self.index:
                    self.index += 1
                if self.game_session.current_user_vk_id == player_id:
                    self._check_round()
                break
        await self.update_game_session()
        return await self.app.store.bj.delete_player_from_game(
            game_session_id=game_session_id, player_id=player_id
        )

    async def round_end(self, game_session_id: int) -> GameSessionModel:
        await self._get_game_session(game_session_id)
        bot = self.get_bot()
        for player in self.game_session.players:
            if (bot.score < player.score < 22) or (player.score < 22 < bot.score):
                player.balance += 2
            else:
                player.balance -= 2
        self._check_game_end()
        return await self.update_game_session()

    async def update_game_session(self) -> GameSessionModel:
        await self.app.store.bj.bulk_update_player(self.game_session.players)
        self.game_session.index = self.index
        return await self.app.store.bj.update_game_session(self.game_session)

    async def _get_game_session(self, game_session_id: int):
        self.game_session = await self.app.store.bj.get_game_session_by_id(
            game_session_id
        )
        if self.game_session:
            self.index = self.game_session.index
        else:
            raise ValueError("Game session not found")

    def _deal_cards(self, count_cards: int):
        for player in self.game_session.players:
            cards = [self.game_session.deck.pop() for _ in range(count_cards)]
            player.hand.extend(cards)
            for card in cards:
                player.score += self._get_point(card, player.score)

    def _clear_scores(self):
        for player in self.game_session.players:
            player.score = 0

    def _clear_hands(self):
        [player.hand.clear() for player in self.game_session.players]

    def _check_turn_player(self, player_id: int):
        if self.game_session.current_user_vk_id != player_id:
            raise ValueError(
                "it's not your turn, actions are expected from {}".format(
                    self.game_session.current_user_vk_id
                )
            )

    def _check_game_end(self) -> bool:
        """Проверка колоды на наличие в ней нужного количества карт для раздачи нового раунда"""
        if len(self.game_session.players) * 2 >= len(self.game_session.deck):
            self.game_session.allowed_actions = ["game end"]
            return True
        self.game_session.allowed_actions = ["new_round"]
        return False

    def _check_round(self) -> bool:
        if self.index >= len(self.game_session.players) or not self.game_session.deck:
            self.game_session.allowed_actions = ["round end"]
            return True
        self.game_session.current_user_vk_id = self.game_session.players[
            self.index
        ].user_id
        return False

    def _check_deal_card(self) -> bool:
        return (
            self.game_session.players[self.index].score < 21 and self.game_session.deck
        )

    def get_bot(self) -> PlayerModel:
        for player in self.game_session.players:
            if player.user_id == 0:
                return player

    @staticmethod
    def _get_point(card: str, scores: int) -> int:
        """Возвращает ценность карты, c учетом Туза"""
        rang = card.split(" ")[1]
        if rang == "A":
            return 11 if (scores + 11) <= 21 else 1
        if rang.isdigit():
            return int(rang)
        return 10
