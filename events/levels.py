from discord import Embed
from discord.ext import commands
from discord.utils import get

from random import randint


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.channel.id in [840555556707237928, 853630887794311178] or \
        message.author.bot or message.author.id == 689154823941390507 or message.content.startswith(self.bot.command_prefix):
            return

        bucket = self.cd.get_bucket(message)
        if bucket.update_rate_limit():
            return

        member = await self.bot.db.members.find({'guilds.id': message.guild.id, '_id': message.author.id}, {'guilds.$': 1})
        if not member:
            return

        xp, lvl = member['guilds'][0]['xp'], member['guilds'][0]['level'] + 1
        next_lvl = 5 / 6 * lvl * (2 * lvl ** 2 + 27 * lvl + 91)

        await self.bot.db.members.update({'guilds.id': message.guild.id, '_id': message.author.id},
                                         {'$inc': {'guilds.$.xp': randint(15, 25), 'guilds.$.level': 1 if xp >= next_lvl else 0}})

        if xp >= next_lvl:
            settings = await self.bot.db.setup.find({'_id': message.guild.id})
            channel = get(message.guild.text_channels, id=settings['channel']) or message.channel
            embed = Embed(description=f'🆙 {message.author.mention} vient de monter niveau **{lvl}**.', color=0xf1c40f)
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Leveling(bot))
