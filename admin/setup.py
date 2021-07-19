from discord import Embed, Role, TextChannel
from discord.ext import commands
from discord.utils import get

from typing import Union


class Setup(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        original = commands.has_permissions(administrator=True).predicate
        return ctx.author.id == 201674460393242624 or await original(ctx)

    @commands.command(
        name='set',
        brief='logs 830846625056292864',
        usage='<mute, mod, logs, testing, channel ou prefix> <valeur>',
        description='Modifier les réglages du bot'
    )
    async def settings_manager(self, ctx, key, value: Union[Role, TextChannel]):
        settings = {
            'mute': 'Rôle des muets',
            'mod': 'Rôle des modérateurs',
            'logs': 'Channel de logs',
            'announce': 'Channel du bot'
        }

        if key not in settings.keys():
            await ctx.send(f'❌ Catégorie invalide : {", ".join(settings.keys())}')
            return

        await self.bot.settings.setv(key, value.id)
        await ctx.send(f'✅ {settings[key]} modifié (**{value.mention}**)')

    @commands.command(
        brief='',
        usage='',
        description='Afficher les réglages du bot'
    )
    async def settings(self, ctx):
        logs = get(ctx.guild.text_channels, id=self.bot.settings.logs)
        announce = get(ctx.guild.text_channels, id=self.bot.settings.announce)

        mute = get(ctx.guild.roles, id=self.bot.settings.mute)
        mod = get(ctx.guild.roles, id=self.bot.settings.mod)

        embed = (Embed(color=0x3498db)
                 .add_field(name='Channel logs', value=f'```#{logs}```')
                 .add_field(name='Channel du bot', value=f'```#{announce}```')
                 .add_field(name='Prochaine baisse de paliers', value=f'```{self.bot.settings.next.strftime("%d/%m/%Y")}```')
                 .add_field(name='Rôle mute', value=f'```@{mute}```')
                 .add_field(name='Rôle modérateur', value=f'```@{mod}```')
                 .set_author(name='Réglages du bot', icon_url=ctx.guild.icon_url))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Setup(bot))
