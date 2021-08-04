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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.db_settings.insert({'guild_id': guild.id, 'mute': None, 'logs': None, 'channel': None})
        await self.bot.db_users.collection.insert_many([{'guild_id': guild.id, 'id': member.id, 'level': 0, 'xp': 0} for member in guild.members if not member.bot])

        await guild.owner.send("Merci beaucoup de m'avoir ajouté 👍" +
                               "\n\nPour certaines de mes commandes, quelques réglages sont nécessaires :" +
                               "\n    • `!set channel <#channel>` pour indiquer au bot ou faire les annonces de level up" +
                               "\n    • `!set logs <#channel>` pour indiquer au bot où envoyer les messages de logs" +
                               "\n\nCes **commandes sont à faire sur ton serveur**, pas ici, en privé ⚠️")

        owner = self.bot.get_user(self.bot.owner_id)
        embed = (Embed(description=f"Owner : {guild.owner.mention}\nNom : {guild.name}\nID : `{guild.id}`", color=0x2ecc71)
                 .set_author(name="J'ai rejoint un serveur", icon_url=guild.icon_url))
        await owner.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.db_settings.delete({'guild_id': guild.id})
        await self.bot.db_users.delete({'guild_id': guild.id})

        owner = self.bot.get_user(self.bot.owner_id)
        embed = (Embed(description=f"Owner : {guild.owner.mention}\nNom : {guild.name}\nID : `{guild.id}`", color=0xe74c3c)
                 .set_author(name="J'ai quitté un serveur", icon_url=guild.icon_url))
        await owner.send(embed=embed)


def setup(bot):
    bot.add_cog(Setup(bot))
