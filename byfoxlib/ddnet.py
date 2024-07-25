import urllib.parse

import numpy
import orjson
from ddapi.deflt import API
from nextcord import Embed, Color
from nextcord.utils import utcnow
from async_lru import alru_cache

from config import channel_id, channel_warning_id, host, message
from .model import SkinRenderData
from .main import checker, get_str

BASEURL = f"https://{host}/api/render"


async def ddnet_warning(self, warning, nicknames):
    timestamp = int(utcnow().timestamp())
    nick = [i[0] for i in nicknames if [1]]
    senders, send = [], False
    for i in warning:
        usr = self.wr.get(i.name)
        if i.name in nick:
            continue
        if usr is None:
            self.wr[i.name] = {"clan": i.clan, 'problem': True, 'send': False, 'timestamp': timestamp + 1800}
            senders.append(f'🔥{i.name}: {i.clan if i.clan != "" else "Клана нет"}🔥 ')
            send = True
        elif not usr['send']:
            senders[-1] += 'f'
        elif usr["problem"] and not timestamp > usr["timestamp"]:
            if i.clan == self.bot.clan_name:
                senders.append(f'🆗{i.name}: {i.clan}🆗')
                del self.wr[i.name]
                send = True
    if send:
        w_ch = self.bot.get_channel(channel_warning_id)
        if w_ch is not None:
            await w_ch.send(
                embed=Embed(title="Warning!", description="\n".join(senders), color=Color.purple()))
        for i in warning:
            self.wr[i.name]['send'] = True
    del senders, send


async def ddnet_global(self, users_, nicknames):
    warning, embeds = [], []

    # member_points, member_online

    users, dat = await checker(self.dd, [i[0] for i in nicknames]), ''

    timestamp = utcnow().strftime("%Y-%m-%d %H:%M:%S+00")
    for type_map, clients in users:
        [await self.bot.DB.edit_tee(client.name, last=timestamp) for client in clients]
        dat += f"``{type_map} - {len(clients)}``\n" + "\n".join(client.name for client in clients) + "\n\n"
        warning.extend([client for client in clients if
                        client.clan != self.bot.clan_name or self.wr.get(client.name, {}).get('problem')])
    for i in numpy.array_split(numpy.array([get_str(count, pl, pp, total) for count, (pl, pp, total) in enumerate(users_, start=1)]), self.count_msg - 1):
        embeds.append('\n'.join(i))
    if not self.msg:
        ch = self.bot.get_channel(channel_id)
        await ch.purge()
        await ch.send(embed=Embed(title=f"{message.clan_members}: {self.bot.clan_name}", color=Color.purple()))
        for i in range(self.count_msg):
            self.msg.append(await ch.send(embed=Embed(title=f"Waiting: {i}")))
    for msg, embed in zip(self.msg, embeds):
        if embed and len(embed) > 1:
            await msg.edit(embed=Embed(description=embed, color=Color.purple()))
    if embeds:
        if len(dat) > 1:
            await self.msg[-1].edit(embed=Embed(description=dat, color=Color.purple()))
    return warning


class SkinRender(API):
    def __init__(self):
        super().__init__(json_loads=orjson.loads)

    @alru_cache(maxsize=32)
    async def get_skin_url(self, name, body=None, feet=None) -> SkinRenderData:
        if name is None:
            return await self._generate(BASEURL + "?skin=default", SkinRenderData)
        params = {"skin": name}
        if body is not None:
            params["body"] = body
        if feet is not None and feet != 255:
            params["feet"] = feet
        param = urllib.parse.urlencode(params)
        return await self._generate(f"{BASEURL}?{param}", SkinRenderData)

