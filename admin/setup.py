from discord import Role, TextChannel, Embed
from discord.ext import commands
from discord.utils import get

from typing import Union


class Setup(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='set',
        brief='channel #🧙-polybot',
        usage='<catégorie> <valeur>',
        description='Modifier les paramètres du bot'
    )
    @commands.has_permissions(administrator=True)
    async def _set(self, ctx, key, value: Union[Role, TextChannel]):
        settings = {
            'mute': 'Rôle des muets',
            'logs': 'Channel de logs',
            'channel': 'Channel du bot'
        }

        if key not in settings:
            print('yes')
            return await ctx.send(f"❌ Catégorie invalide : {', '.join(settings.keys())}")

        await self.bot.db_settings.update({'guild_id': ctx.guild.id}, {'$set': {key: value.id}})
        await ctx.send(f"{settings[key]} modifié ({value.mention})")

    @commands.command(
        brief='',
        usage='',
        description='Afficher les paramètres du bot'
    )
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        settings = await self.bot.db_settings.find({'guild_id': ctx.guild.id})
        mute = get(ctx.guild.roles, id=settings['mute'])
        channel = get(ctx.guild.text_channels, id=settings['channel'])
        logs = get(ctx.guild.text_channels, id=settings['logs'])

        embed = (Embed(color=0x3498db)
                 .add_field(name='Channel des logs', value=f'```#{logs}```')
                 .add_field(name='Channel du bot', value=f'```#{channel}```')
                 .add_field(name='Rôle des mutés', value=f'```@{mute}```'))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Setup(bot))
