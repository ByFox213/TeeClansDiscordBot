import io
import os
from typing import TypeVar
from urllib.parse import quote

import orjson
import yaml
from ddapi import DDnetApi, Master
from nextcord import Member, Role, File

from config import clan_name


DateClassT = TypeVar("DateClassT", bound="dateclass")


def get_search(member: Member | None, user: Member, tee: str | None) -> str | int:
    if member is not None:
        return member.id
    if tee is not None:
        return tee
    return user.id


async def checker(obj: DDnetApi, nicknames: list[str]) -> list:
    ms: Master = await obj.master()
    cll = []
    nicknames = [i.lower() for i in nicknames]
    for i in ms.servers:
        q = [client for client in i.info.clients if client.name in nicknames or client.clan == clan_name]
        if q:
            cll.append([f"{i.info.name}: {i.info.map.get('name', '')}", q])
    return cll


def check_roles_for_id(roles_member: list[Role], roles: list[int]) -> bool:
    member_roles = [i.id for i in roles_member]
    for i in roles:
        if i in member_roles:
            return True
    return False


def get_url(player: str) -> str:
    return f"https://ddstats.tw/player/{quote(player).replace('/', '-47-')}"


def get_str(count: int | str,
            player: str,
            pp: int | str,
            total: int | str,
            _str: str = None) -> str:
    # graph = ''
    # if int(count) < 6:
    # graph = f"| {create_graph_emoji((points/pp)*100, 5)}"
    if _str is None:
        _str = "{count}. [{player}]({url})"
    return _str.format(count=count, player=player, pp=pp, total=total, url=get_url(player))


class Loads:
    @staticmethod
    def loads_yaml(filename: str,
                   dc: DateClassT,
                   example_date: str = None,
                   rt: any = None) -> DateClassT | any:
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as file:
                if example_date is not None:
                    file.write(example_date)
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        if data is None:
            return rt
        return dc(**data)

    @staticmethod
    def loads_json(filename: str,
                   dc: DateClassT,
                   example_date: str = None,
                   rt: any = None) -> DateClassT | any:
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as file:
                if example_date is not None:
                    file.write(example_date)
        with open(filename, "r", encoding="utf-8") as file:
            data = orjson.loads(file.read())
        if data is None:
            return rt
        return dc(**data)


def text_to_file(text: str, filename: str = "text.txt", **kwargs) -> File:
    return File(io.StringIO(text), filename=filename, **kwargs)
