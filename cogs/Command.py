import nextcord
from ddapi import DDnetApi, DDstats
from nextcord import Interaction, Member, Embed, Color, SlashOption
from nextcord.ext import commands

from byfoxlib import join_dt, get_search, SkinRender
from byfoxlib.model import TeeDat
from config import message


class Command(commands.Cog):
    def __init__(self, **_):
        self.skin = SkinRender()
        self.dd: DDnetApi = DDnetApi()
        self.ddstat: DDstats = DDstats()
        self.perms = {
            0: message.member,
            1: message.moder,
            2: message.deputy,
            4: message.chapter,
            5: message.programmer
        }

    @nextcord.slash_command(dm_permission=False)
    async def remove_member(self, im: Interaction,
                            member: Member = SlashOption(required=False),
                            tee: str = SlashOption(required=False)):
        if member is None and tee is None:
            return await im.send(embed=Embed(title=message.forgot2, color=Color.red()), ephemeral=True)
        search = tee
        if member is not None:
            search = member.id
            if member.bot:
                return await im.send(embed=Embed(title=message.memberisbot, color=Color.red()), ephemeral=True)
        if await im.client.check_perm(im, search, False):
            mem = await im.client.remove_member(im.guild, member, search, remove=True)
            if not isinstance(mem, TeeDat) and not mem:
                return await im.send(embed=Embed(title=message.something, color=Color.red()), ephemeral=True)
            ch = im.guild.get_channel(1251483757698093126)
            if ch is not None and mem is not None:
                await ch.send(embed=Embed(title=message.remove_user, description=f"{message.remove}: <@{mem.member_id}>\nBy {im.user.name}({im.user.id})", color=Color.red()))
            await im.client.update_status()
            return await im.send(embed=Embed(title=message.player_remove, color=Color.green()), ephemeral=True)

    @nextcord.slash_command(dm_permission=False)
    async def member(self, im: Interaction, member: Member = None, tee: str = None):
        await im.response.defer(ephemeral=True)
        if member is not None and member.bot:
            return await im.send(embed=Embed(title=message.memberisbot, color=Color.red()))
        search = get_search(member, im.user, tee)
        user = await im.client.DB.get_tee(search)
        if user is None:
            return await im.send(embed=Embed(title=message.notreg, color=Color.red()))
        timestamp, mention = '', ''
        if member is None:
            member = im.guild.get_member(user.member_id)
        if member is not None:
            mention = f'({member.mention})'
        if str(user.last_played) != "1970-01-01 00:00:00":
            timestamp = f'Последний заход: {join_dt(user.last_played)}'

        pp, points = await self.dd.player(user.nickname), ''
        if pp is not None and pp.points is not None:
            points = f'| {pp.points.points}'
        g_player = await self.ddstat.player(user.nickname)
        profile = None
        if g_player is not None:
            profile = g_player.profile

        embed = Embed(description=f"Игрок: {user.nickname}{mention} {points}\nПрава доступа: {self.perms.get(user.perms, 'Какой-то хуй с высокими правами')}\n\n{timestamp}", color=Color.green())

        us = None
        if profile is not None:
            us = await self.skin.get_skin_url(profile.skin_name, profile.skin_color_body, profile.skin_color_feet)

        if us is not None and us.url is not None:
            embed.set_thumbnail(url=us.url)
        return await im.send(embed=embed)
