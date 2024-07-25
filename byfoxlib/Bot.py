# -*- coding: utf-8 -*-
import logging
from typing import Any, Union

import nextcord
import psycopg2
from nextcord import ActivityType, Status, Interaction, Embed, Color, Member, Guild, Permissions
from nextcord.ext import commands
from nextcord.utils import utcnow

__all__ = (
    "DB",
    "Bot",
    "FuncomBotInter"
)

from config import member_role
from .model import TeeDat, Lang


class FuncomBotInter(Interaction):
    def __init__(self, *, data, state):
        super().__init__(data=data, state=state)

    @property
    def bot_perms(self) -> Permissions:
        return self.guild.me.guild_permissions

    @property
    def perms(self) -> Permissions:
        return self.user.guild_permissions

    @property
    def admin(self) -> bool:
        return self.perms.administrator or self.bot_owner

    @property
    def bot_owner(self) -> bool:
        return self.user.id in self.client.owner_ids

    @property
    def owner(self) -> bool:
        if self.guild is not None and self.guild.owner is not None:
            return self.user.id == self.guild.owner.id
        return False

    def get_langs(self) -> Lang:
        cl = self.client.lang
        data = cl.get(self.locale, None)
        if data is None:
            data = cl["en"]
        return data


def escape(text: Any) -> str:
    text = str(text)
    for i, o in [['\'', ''], ['\"', ''], ['\\', '']]:
        text = text.replace(i, o)
    return text
    # return re.escape(str(text))


class DB:
    def __init__(self, con: str):
        self.con: str = con
        self._log = logging.getLogger(__name__)

        self.post = None
        self.check_connect()

    def check_connect(self) -> bool:
        if self.post is not None and not self.post.closed:
            return False
        self.post = psycopg2.connect(self.con)
        self._log.info("postgresql connect")
        self.post.set_session(autocommit=True)
        # self.post.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return True

    async def get_tee(self, select: any = None, limit: int = 1, search: list = None) -> Union[None, TeeDat, list[TeeDat]]:
        if search is None:
            search = []
        if isinstance(select, int):
            search.append(f"\"member_id\" = \'{select}\'")
        elif isinstance(select, str):
            search.append(f"\"nickname\" = \'{escape(select)}\'")
        with self.post.cursor() as cur:
            cur.execute(f"SELECT member_id, nickname, perms, last_played, ignore from users {'where' if search else ''} {' and '.join(search)} limit {limit}")
            if limit == 1:
                data = cur.fetchone()
                if not data:
                    return
                member_id, nickname, perms, last_played, ignore = data
                return TeeDat(member_id=member_id, nickname=nickname, perms=perms, ignore=ignore, last_played=last_played)
            data = cur.fetchmany(limit)
            rt = []
            for i in data:
                member_id, nickname, perms, last_played, ignore = i
                rt.append(TeeDat(member_id=member_id, nickname=nickname, perms=perms, ignore=ignore, last_played=last_played))
            return rt

    async def get_count_tee(self) -> int | None:
        with self.post.cursor() as cur:
            cur.execute("SELECT COUNT(\"nickname\") from users where \"perms\" < 6 limit 1")
            data = cur.fetchone()
            if not data:
                return
            return data[0]

    async def add_tee(self, member_id: int, nickname: str) -> bool:
        te = await self.get_tee(member_id)
        if te is not None:
            return False
        sql = member_id, escape(nickname),
        self._log.info("add_tee(%s)", sql)
        with self.post.cursor() as cur:
            cur.execute("INSERT INTO users (member_id, nickname) VALUES (%s, %s)", sql)
        return True

    async def remove_tee(self, member_id: int):
        self._log.info("remove_tee(%s)", member_id)
        with self.post.cursor() as cur:
            cur.execute("DELETE FROM users WHERE member_id = %s;", member_id)
        return True

    async def edit_tee(self,
                       select: any = None,
                       nickname: str = None,
                       perms: int = None,
                       ignore: bool = None,
                       last: str = None) -> bool:
        update_str = []
        if isinstance(select, int):
            select = f"\"member_id\" = \'{select}\'"
        elif isinstance(select, str):
            select = f"\"nickname\" = \'{escape(select)}\'"
        for a, n in [(nickname, "nickname"), (perms, "perms"), (ignore, "ignore"), (last, "last_played")]:
            if a is not None:
                update_str.append(f"\"{n}\" = '{a}'")
        if len(update_str) < 1:
            return False
        upd = ', '.join(update_str)
        self._log.info("edit_tee(%s)", (upd, ))
        with self.post.cursor() as cur:
            cur.execute(f"Update users set {upd} where {select}")
        return True


class Bot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.ready_ran = False

        # get var
        self.app = {}

        self.lang = kwargs.pop("lang")
        self.clan_name = kwargs.pop("clan_name")
        self.DB = DB(con=kwargs.pop("con"))

        super().__init__(*args, **kwargs)

    def get_interaction(self, data, *, cls=Interaction):
        return super().get_interaction(data, cls=FuncomBotInter)

    async def update_status(self):
        await self.change_presence(
            activity=nextcord.Activity(
                type=ActivityType.watching,
                name="Клан: {0}".format(await self.DB.get_count_tee())),
            status=Status.online
        )

    async def check_perm(self, im: Interaction, select: any, check_register: bool = True):
        if im.user == im.guild.owner or im.user.id in self.owner_ids:
            return True
        editor = await self.DB.get_tee(im.user.id)
        user = await self.DB.get_tee(select)
        if check_register and user is not None:
            await im.send(embed=Embed(title="Данный пользователь уже зарегестрирован", color=Color.red()),
                          ephemeral=True)
            return False
        perm = 0
        if user is not None:
            perm = user.perms
        if editor is None or editor.perms <= perm:
            await im.send(embed=Embed(title="У вас недостаточно прав", color=Color.red()),
                          ephemeral=True)
            return False
        return True

    async def add_member(self, member: Member, nickname: str) -> TeeDat | None | bool:
        mm = await self.DB.get_tee(member.id)
        if member.name.lower() != nickname.lower():
            await member.edit(nick=nickname)
        if mm is None:
            await self.DB.add_tee(member.id, nickname=nickname)
        return mm

    async def remove_member(self, guild: Guild, member: Member, search: any) -> TeeDat | None | bool:
        mem = await self.DB.get_tee(search)
        if member is None and mem is not None:
            member = guild.get_member(mem.member_id)
        if member is not None:
            member_roles = [i.id for i in member.roles]
            if member_role in member_roles:
                await member.remove_roles(guild.get_role(member_role))
        res = await self.DB.remove_tee(mem.member_id)
        if not res:
            return False
        return mem
