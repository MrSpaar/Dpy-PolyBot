from discord import Role, TextChannel, Embed
from discord.ext import commands
from discord.utils import get

from typing import Union
from os import listdir


class SetupCommands(commands.Cog, name='Configuration', description='admin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='set',
        brief='channel #🧙-polybot',
        usage='<mute, logs ou channel> <@role ou #channel>',
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
            embed = Embed(color=0xe74c3c, description=f"❌ Catégorie invalide : {', '.join(settings.keys())}")
            return await ctx.send(embed=embed)

        await self.bot.db.setup.update({'_id': ctx.guild.id}, {'$set': {key: value.id}})

        embed = Embed(color=0x2ecc71, description=f"{settings[key]} modifié ({value.mention})")
        await ctx.send(embed=embed)

    @commands.command(
        brief='',
        usage='',
        description='Afficher les paramètres du bot'
    )
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        settings = await self.bot.db.setup.find({'_id': ctx.guild.id})

        channel = getattr(get(ctx.guild.text_channels, id=settings['channel']), 'mention', 'pas défini')
        logs = getattr(get(ctx.guild.text_channels, id=settings['logs']), 'mention', 'pas défini')
        mute = getattr(get(ctx.guild.roles, id=settings['mute']), 'mention', 'pas défini')

        embed = Embed(color=0x3498db, description=f"💬 Bot : {channel}\n📟 Logs : {logs}\n🔇 Mute : {mute}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        for directory in ['admin', 'events', 'commands']:
            for file in listdir(directory):
                if file != '__pycache__' and not (file in ['errors.py', 'logs.py'] and self.bot.debug):
                    self.bot.reload_extension(f'{directory}.{file[:-3]}')

        embed = Embed(color=0x2ecc71, description='✅ Tous les modules ont été relancé')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SetupCommands(bot))
