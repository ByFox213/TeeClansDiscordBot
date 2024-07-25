import nextcord
from nextcord import TextInputStyle, Button, ButtonStyle, Embed, Color
from nextcord.ui import Modal, TextInput, View
from ddapi import DDnetApi, DDstats

from .Bot import FuncomBotInter
from .model import TeeDat
from .ddnet import SkinRender
from config import clan_name, application, member_role


class Application(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.skin = SkinRender()
        self.ddapi = DDnetApi()
        self.ddstat = DDstats()

    @nextcord.ui.button(label="Submit", emoji="🦊", style=ButtonStyle.green)
    async def application(self, _: Button, interaction: FuncomBotInter):
        modal = ClanJoin(self.ddapi, self.ddstat, self.skin)
        await interaction.response.send_modal(modal)


class Confirm(nextcord.ui.View):
    def __init__(self, im, nick):
        super().__init__(timeout=None)
        self.im: FuncomBotInter = im
        self.nick: str = nick

    @nextcord.ui.button(label="Принять", style=ButtonStyle.green)
    async def confirm(self, _: Button, im: FuncomBotInter):
        user = im.guild.get_member(self.im.user.id)
        if user is None:
            await im.message.edit(content="Пользователь не найден", view=None)
            self.stop()
            return await im.send(embed=Embed(title="Пользователь не найден", description="Причиной того могло быть:\n- Пользователь вышел с сервера\n- У бота недостаточно прав", color=Color.red()))
        if member_role not in [i.id for i in user.roles]:
            await user.add_roles(im.guild.get_role(member_role))
        await im.client.add_member(self.im.user, self.nick)
        await user.send(embed=Embed(title="Ваше заявление было принято", description="Удачи в игре с кланом", color=Color.green()))
        await im.send(embed=Embed(title="Пользователь принят", color=Color.green()), ephemeral=True)
        ch = im.guild.get_channel(1251483757698093126)
        if ch is not None:
            await ch.send(embed=Embed(title="Add member", description=f"добавлен: {self.nick}({self.im.user.mention})\nBy {im.user.name}({im.user.id})", color=Color.green()))
        await im.client.update_status()
        await im.message.edit(view=None)
        del im.client.app[user.id]
        self.stop()

    @nextcord.ui.button(label="Отказать", style=ButtonStyle.grey)
    async def cancel(self, _: Button, im: FuncomBotInter):
        user = im.guild.get_member(self.im.user.id)
        if user is None:
            await im.message.edit(content="Пользователь не найден", view=None)
            self.stop()
            return await im.send(embed=Embed(title="Пользователь не найден", color=Color.red()))
        await user.send(embed=Embed(title="EN\nYour application has been rejected\n\nRU\nВаше заявление было отклонено", color=Color.red()))
        await im.send(embed=Embed(title="Пользователь отклонен", color=Color.green()), ephemeral=True)
        await im.message.edit(view=None)
        del im.client.app[user.id]
        self.stop()


class ClanJoin(Modal):
    def __init__(self, ddapi, ddstat, skin):
        super().__init__(
            f"Заявка в клана: {clan_name}",
            timeout=1200
        )
        self.skin: SkinRender = skin
        self.ddapi: DDnetApi = ddapi
        self.ddstat: DDstats = ddstat

        self.nick = TextInput(label="Никнейм", min_length=1, max_length=15, style=TextInputStyle.short, placeholder="Funcom♪")
        self.age = TextInput(label="Вохраст", min_length=1, max_length=2, style=TextInputStyle.short, placeholder="15")
        self.about_user = TextInput(label="Расскажите о себе",  style=TextInputStyle.paragraph, required=False, min_length=1, max_length=500)
        self.add_item(self.nick)
        self.add_item(self.age)
        self.add_item(self.about_user)

    async def callback(self, im: FuncomBotInter):
        await im.response.defer(ephemeral=True)

        locale = im.get_langs().modal
        if im.client.app.get(im.user.id, False):
            return await im.send(embed=Embed(title=locale.wait, color=Color.red()))

        te: TeeDat = await im.client.DB.get_tee(im.id)
        if te is not None:
            return await im.send(embed=Embed(title=locale.registred))

        ch = im.guild.get_channel(application.get("mod_channel"))
        if ch is None:
            return

        age = self.age.value
        if not age.isnumeric():
            return await im.send(embed=Embed(title=locale.agenotallow))

        if int(age) < 13:
            await ch.send(embed=Embed(title=f"Репорт на {im.user.name}({im.user.id})", description="Нарушение правил Discord, участнику меньше 13-цети лет", color=Color.red()))

        # get_player_data

        player = await self.ddapi.player(self.nick.value)
        g_player = await self.ddstat.player(self.nick.value)
        profile = None
        if g_player is not None:
            profile = g_player.profile

        # обработка

        pp, about = 'Не обнаружены' if player is None or player.points is None else player.points.points, ''

        val = self.about_user.value
        if val is not None:
            about = "О пользователе: " + self.about_user.value
        embed = Embed(description=f"Заявка от {im.user.name}({im.user.id}), возраст: {age}\nНик: {self.nick.value}; pp: {pp}\n{about}", color=Color.purple())

        us = None
        if profile is not None:
            us = await self.skin.get_skin_url(profile.skin_name, profile.skin_color_body, profile.skin_color_feet)
        
        if profile is not None and us is not None and us.url is not None:
            embed.set_thumbnail(url=us.url)

        confirm = Confirm(im, self.nick.value)
        await ch.send(embed=embed, view=confirm)
        await im.send(embed=Embed(title=locale.sended, description=locale.wait_moder, color=Color.purple()), ephemeral=True)
        im.client.app[im.user.id] = True
