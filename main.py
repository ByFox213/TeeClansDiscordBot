import asyncio
import logging

import nextcord
from nextcord.utils import utcnow

from byfoxlib import get_token, load_cog, Bot, get_language
from config import sql, clan_name

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

date = utcnow().strftime("%Y.%m.%d")
logging.basicConfig(level=logging.INFO, filename=f"discord_bot.log", format='%(asctime)s:%(levelname)s:%(name)s: %(message)s', encoding='utf-8', filemode="w")

bot: Bot = Bot(
    intents=nextcord.Intents.all(),
    owner_ids=[435836413523787778],
    con=str(sql),
    clan_name=clan_name,
    lang=get_language()
)

if __name__ == '__main__':
    load_cog(bot)
    bot.run(get_token())
