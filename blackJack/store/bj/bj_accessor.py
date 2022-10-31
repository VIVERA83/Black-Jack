from base.base_accessor import BaseAccessor
from bj.models import GameSessionModel, PlayerModel, StatusGameEnum, StatusPlayerEnum
from sqlalchemy import bindparam, select, update, delete, and_
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.orm import selectinload
from store.bj.utils import create_deck


class BJAccessor(BaseAccessor):
    async def create_game_session(
        self, players_id: list[int], count_deck: int, initial_balance: int
    ) -> GameSessionModel:
        """
        Создается и кладется в БД Игровая сессия игры, так же добавляется Бот(Крупье).
        :param players_id: список id игроков, имеется ввиду id из vk.
        :param count_deck: размер колоды, из скольки колод будет состоять одна большая колода.
        :param initial_balance: начальны балан очков(фишек) при старте игры, для всех одинаково.
        :return:
        """
        async with self.app.database.session.begin() as session:
            players_id.append(0)  # Крупье
            game_sessions = GameSessionModel(
                index=0,
                current_user_vk_id=players_id[0],
                deck=create_deck(count_deck),
                status_game=StatusGameEnum.active,
                players=[
                    PlayerModel(
                        user_id=id_,
                        balance=initial_balance,
                        score=0,
                        hand=[],
                        status=StatusPlayerEnum.active,
                    )
                    for id_ in players_id
                ],
                players_list=players_id,
                allowed_actions=["new round"],
            )
            session.add(game_sessions)
            return game_sessions

    async def get_game_session_by_id(self, game_session_id: int) -> GameSessionModel:
        async with self.app.database.session.begin() as session:
            chang: ChunkedIteratorResult = await session.execute(
                select(GameSessionModel)
                .options(selectinload(GameSessionModel.players))
                .where(GameSessionModel.id == game_session_id)
            )
            return chang.scalars().first()

    async def get_player_by_id(self, player_id: int) -> PlayerModel:
        async with self.app.database.session.begin() as session:
            chang: ChunkedIteratorResult = await session.execute(
                select(PlayerModel).where(PlayerModel.id == player_id)
            )
            return chang.scalars().first()

    async def update_game_session(
        self, game_session: GameSessionModel
    ) -> GameSessionModel:
        async with self.app.database.session.begin() as session:
            await session.execute(
                update(GameSessionModel)
                .where(GameSessionModel.id == game_session.id)
                .values(
                    index=game_session.index,
                    current_user_vk_id=game_session.current_user_vk_id,
                    deck=game_session.deck,
                    status_game=game_session.status_game,
                    players_list=game_session.players_list,
                    allowed_actions=game_session.allowed_actions,
                )
            )

        return await self.get_game_session_by_id(game_session.id)

    async def bulk_update_player(self, players: list[PlayerModel]) -> list[PlayerModel]:
        async with self.app.database.session.begin() as session:
            await session.execute(
                update(PlayerModel)
                .where(PlayerModel.id == bindparam("b_id"))
                .values(hand=bindparam("hand"), score=bindparam("score"))
                .returning(PlayerModel),
                [
                    {
                        "b_id": player.id,
                        "hand": player.hand,
                        "score": player.score,
                        "balance": player.balance,
                    }
                    for player in players
                ],
            )
        return players

    async def delete_player_from_game(
        self, game_session_id: int, player_id: int
    ) -> GameSessionModel:
        async with self.app.database.session.begin() as session:
            await session.execute(
                delete(PlayerModel).where(
                    and_(
                        PlayerModel.game_session_id == game_session_id,
                        PlayerModel.user_id == player_id,
                    )
                )
            )
        return await self.get_game_session_by_id(game_session_id)
