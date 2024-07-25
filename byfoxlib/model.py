from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


@dataclass
class Post:
    host: str
    port: int
    user: str
    passwd: str
    db: str

    def __str__(self) -> str:
        return f"dbname={self.db} host={self.host} port={self.port} user={self.user} password={self.passwd}"


class TeeWorldsData(BaseModel):
    prefix: str
    systemctl: list[str]


class SkinRenderData(BaseModel):
    err: str = None
    url: str = None


class TeeDat(BaseModel):
    member_id: int
    nickname: str
    perms: int
    last_played: datetime
    ignore: bool


class Modal(BaseModel):
    wait: str
    registred: str
    sended: str
    wait_moder: str
    agenotallow: str


class Lang(BaseModel):
    modal: Modal


class BotMessage(BaseModel):
    clan_app: str
    clan_desk: str
    remove_user: str
    remove: str
    leave_user: str
    error: str
    member: str
    moder: str
    deputy: str
    chapter: str
    programmer: str
    forgot2: str
    memberisbot: str
    something: str
    player_remove: str
    notreg: str
    clan_members: str
