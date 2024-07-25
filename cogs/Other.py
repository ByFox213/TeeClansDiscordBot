import logging
from asyncio import sleep

from ddapi import DDnetApi
from nextcord import Member, Embed, Message, Color
from nextcord.ext import commands

from byfoxlib import Bot, ddnet_global, Application, ddnet_warning
from config import err_channel, application, message


class Other(commands.Cog):
    def __init__(self, bot: Bot, **_):
        self._log = logging.getLogger(__name__)
        self.bot: Bot = bot

        # ddapi

        self.dd = DDnetApi()

        # settings

        self.count_msg = 2
        self.msg: list[Message] = []
        self.ready = False
        self.wr = {}

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ready:
            print(f"| start {self.bot.user} (ID: {self.bot.user.id})")
            await self.bot.update_status()

            # send_application

            ch = self.bot.get_channel(application.get("channel"))
            await ch.purge(limit=10)

            embed = Embed(title=f"{message.clan_app}: {self.bot.clan_name}", description=message.clan_desk, color=Color.purple()).set_footer(text="ByFox system creator")

            app = Application()
            await ch.send(embed=embed, view=app)

            await self.bot.loop.create_task(self.stats_update())
            self.ready: bool = True

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        mem = await self.bot.DB.get_tee(member.id)
        if mem is None:
            return
        await self.bot.DB.edit_tee(member.id)
        ch = member.guild.get_channel(1251483757698093126)
        if ch is not None:
            await ch.send(embed=Embed(title=message.remove_user, description=f"{message.leave_user}: {mem.tee}({member.mention})"))

    @commands.Cog.listener()
    async def on_http_ratelimit(self, limit, remaining, reset_after, bucket, scope):
        print(f"| ratelimit: {limit}, {remaining}, {reset_after}, {bucket}, {scope}")

    @commands.Cog.listener()
    async def on_application_command_error(self, _, error):
        err_chanel = self.bot.get_channel(err_channel)
        if err_chanel is None:
            return
        logging.exception(error)
        embed: Embed = Embed(title=message.error, description=str(error), color=Color.red())
        return await err_chanel.send(embed=embed)

    async def stats_update(self):
        while True:
            try:
                nicknames = [(i.nickname, i.ignore) for i in await self.bot.DB.get_tee(limit=500, search=["\"perms\" < 6"])]
                users = sorted([
                    [p.player, p.points.points, p.points.total] if p is not None else [n, -1, 9999]
                    for p, n in
                    [[await self.dd.player(i[0]), i[0]] for i in nicknames]
                ], key=lambda x: x[1], reverse=True)

                warning = await ddnet_global(self, users, nicknames)
                if warning:
                    await ddnet_warning(self, warning, nicknames)
            except Exception as ex:
                print(f"{type(ex)}: {ex}")
            await sleep(600)
