from typing import Self

from models.mongo import MongoModel, me
from datetime import datetime
from __future__ import annotations


class Match(me.Document, MongoModel):
    starts: datetime = me.DateTimeField(required=True)
    blind_increasing =me.IntField()
    rounds_until_blind_increase = me.IntField()
    ends: datetime = me.DateTimeField()
    level: int = me.IntField()
    final_ranking = me.ListField(me.IntField()) # list of user ids
    players_per_table = me.IntField(min_value=0)
    match_players = me.IntField(min_value=0)
    tables: list[Table] = me.ListField(me.EmbeddedDocumentField(Table))

    def get_match_players(self, squalified_players:dict[int, dict] ) -> dict[int, dict]:
        players = {k: v for table in self.tables for k, v in table.players.items() if k not in squalified_players}
        return dict(sorted(players.items(), key=lambda item: item[1]['fish'], reverse=True))


    class Table(me.EmbeddedDocument):
        match: Match = me.ReferenceField('Match', reverse_delete_rule=me.CASCADE)
        big_blind = me.IntField(required=True)
        small_blind = me.IntField()
        players = me.MapField(me.DictField(), required=True)
        amount_to_call = me.IntField(min_value=0)
        rounds_at_current_blind = me.IntField(min_value=0)
        last_players_played = me.IntField(min_value=1)  # player user id
        players_left_to_act = me.IntField(min_value=0)
        pot = me.IntField(min_value=0)
        all_in_users = me.ListField(me.IntField, default=[])

        @classmethod
        def get_table_by_players(cls, players: list[int]) -> Match.Table:
            return cls.objects.filter(**{f"players.{player_id}": {"$exists": True} for player_id in players}).first()

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.small_blind = self.big_blind / 2
            self.rounds_at_current_blind = 0

        def __pay_blinds(self) -> None:
            def pay_blinds(blind: str):
                user_key = 'is_' + blind
                self.players[current_user_id] = {key: val for key, val in self.players[current_user_id] if
                                                 not val == user_key}
                self.players[previous_user_id][user_key] = 1
                if getattr(self, blind) >= self.players[previous_user_id]['fish']:
                    self.pot += self.players[previous_user_id]['fish']
                    self.all_in_users.append(previous_user_id)
                else:
                    self.pot += getattr(self, blind)
                    self.players[previous_user_id]['fish'] -= getattr(self, blind)

            users_id = list(self.players.keys())
            if self.big_blind == self.match.blind_increasing and not self.rounds_at_current_blind:  # is first round of game
                self.players[users_id[-1]]['is_big_blind'] = 1
                self.players[users_id[-1]]['fish'] -= self.big_blind
                self.players[users_id[-2]]['is_small_blind'] = 1
                self.players[users_id[-2]]['fish'] -= self.small_blind
                self.pot = self.big_blind + self.small_blind
                return
            for i, current_user_id, player in enumerate(self.players.items()):
                previous_user_id = users_id[i - 1]
                if 'is_big_blind' in player:
                    pay_blinds('big_blind')
                elif 'is_small_blind' in player:
                    pay_blinds('small_blind')

        def __start_round(self) -> Self:
            if self.rounds_at_current_blind == self.match.rounds_until_blind_increase:
                self.rounds_at_current_blind = 0
                self.big_blind += self.match.blind_increasing
                self.small_blind = self.big_blind / 2
                self.__pay_blinds()
            else:
                self.__pay_blinds()
                self.rounds_at_current_blind += 1
            self.players_left_to_act = len(self.players)
            self.last_players_played = None
            self.save()
            return self

        def __end_round(self, winner_user_id: int)-> Self:
            # TODO: store on db the players cards and find the winner so that you avoid passing it as parameter
            if not winner_user_id or not winner_user_id in self.players:
                raise InvalidUserId("the user provided can't be a winner as it did not take part to the table")

            self.players[winner_user_id]['fish'] += self.pot
            self.pot = 0

            if not self.all_in_users:
                return

            users_to_delete = {user_id: player for user_id, player in self.players.items() if
                               user_id in set(self.all_in_users).difference(winner_user_id)}
            for user_id in users_to_delete:
                self.match.final_ranking.insert(0, user_id)
            self.match.save()

            self.players = {user_id: player for user_id, player in self.players.items() if
                            user_id not in users_to_delete}

            self.match.match_players -= len(users_to_delete)
            necessary_tables_num = self.match.match_players // self.match.players_per_table
            if necessary_tables_num >= len(self.match.tables):
                self.save()
                return

            players = self.match.get_match_players(users_to_delete)
            players_id = players.keys()
            tables_to_keep = self.match.tables[:necessary_tables_num]
            tables_to_delete = self.match.tables[necessary_tables_num:]

            user_per_table = len(players) // len(tables_to_keep)
            for i, table in tables_to_keep:
                table.players = {
                    key: {
                        k: v for k, v in players[key].items() if k not in ['is_big_blind', 'is_small_blind']
                    }
                    for key in players_id[i:self.match.players_num:user_per_table]
                }
                table.save()

            for table in tables_to_delete:
                table.delete()
            self.players.match.final_ranking.extend(list(users_to_delete.keys()))
            self.save()

        @classmethod
        def handle_round(cls, players: list[int], round_: str = 'start', winner_user_id: int | None = None) -> Self:
            table = cls.get_table_by_players(players)
            if not table or not table.match:
                raise RowNotFound("no match has a table with the given users")
            return table.__start_round() if round_ == 'start' else table.__end_round(winner_user_id)

        def __raise(self, user_id: int, raised_amount: int):
            if self.players[user_id]['fish'] < self.amount_to_call:
                raise InsufficientMoney("you do not have money to call the raise/bet of the opponent")
            raised_amount += self.amount_to_call
            if self.players[user_id]['fish'] < raised_amount:
                raise InsufficientMoney("you do not have enough money to make that raise")
            self.amount_to_call = raised_amount
            self.players[user_id]['fish'] -= raised_amount
            self.pot += raised_amount
            self.save()

        def __call(self, user_id:int):
            if self.players[user_id]['fish'] < self.amount_to_call:
                self.__all_in(user_id)
            self.players[user_id]['fish'] -= self.amount_to_call
            self.pot += self.amount_to_call
            self.save()

        def __all_in(self, user_id:int):
            self.__raise(user_id, self.players[user_id]['fish'])
            self.all_in_users.append(user_id)

        def __bet(self, user_id: int, bet_amount):
            if bet_amount > self.players[user_id]['fish']:
                raise InsufficientMoney()
            self.amount_to_call = bet_amount
            if bet_amount == self.players[user_id]['fish']:
                self.__all_in(user_id)
            else:
                self.pot += bet_amount
                self.players[user_id]['fish'] -=bet_amount
                self.save()

        # TODO: implement fold and check method


        @classmethod
        def handle_hand(cls, user_id: int, raised_amount: int| None=None, is_all_in:bool = False):
            table = cls.get_table_by_players([user_id])
            if is_all_in:
                cls.__all_in(user_id)
            elif raised_amount and hasattr(table, 'amount_to_call'):
                cls.__raise(user_id, raised_amount)
            elif hasattr(table, 'amount_to_call'):
                cls.__call(user_id)
            else:
                cls.__bet(user_id, raised_amount)
