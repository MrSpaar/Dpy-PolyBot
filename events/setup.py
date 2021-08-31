from discord import Embed
from discord.ext import commands


class SetupEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.db.settings.insert({'guild_id': guild.id, 'mute': None, 'logs': None, 'channel': None, 'new': []})
        for member in filter(lambda m: not m.bot, guild.members):
            await self.bot.db.members.update({'_id': member.id}, {'$addToSet': {'guilds': {'id': guild.id, 'level': 0, 'xp':0}}}, True)

        await guild.owner.send("Merci beaucoup de m'avoir ajouté 👍" +
                               "\n\nPour certaines de mes commandes, quelques réglages sont nécessaires :" +
                               "\n    • `!set channel <#channel>` pour indiquer au bot ou faire les annonces de level up" +
                               "\n    • `!set logs <#channel>` pour indiquer au bot où envoyer les messages de logs" +
                               "\n\nCes **commandes sont à faire sur ton serveur**, pas ici, en privé ⚠️")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.db.settings.delete({'guild_id': guild.id})
        await self.bot.db.members.collection.update_many({'_id': {'$in': [member.id for member in guild.members]}}, {'$pull': {'guilds': {'id': guild.id}}})

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.db.members.update({'_id': member.id}, {'$addToSet': {'guilds': {'id': member.guild.id, 'level': 0, 'xp': 0}}}, True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.db.members.update({'_id': member.id}, {'$pull': {'guilds': {'id': member.guild.id}}})

def setup(bot):
    bot.add_cog(SetupEvents(bot))
