from discord import Embed
from discord.ext import commands
from discord.utils import get

from random import randint


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.channel.id in [840555556707237928, 853630887794311178] or message.author.bot:
            return

        bucket = self.cd.get_bucket(message)
        if bucket.update_rate_limit():
            return

        member = await self.bot.db.users.find({'guild_id': message.guild.id, 'id': message.author.id})
        if not member:
            return

        xp, lvl = member['xp'] + (randint(15, 25)), member['level'] + 1
        next_lvl = 5 / 6 * lvl * (2 * lvl ** 2 + 27 * lvl + 91)

        await self.bot.db.users.update({'guild_id': message.guild.id, 'id': message.author.id},
                                       {'$set': {'xp': int(xp), 'level': lvl if xp >= next_lvl else lvl - 1}})

        if xp >= next_lvl:
            settings = await self.bot.db.settings.find({'guild_id': message.guild.id})
            channel = get(message.guild.text_channels, id=settings['channel']) or message.channel
            embed = Embed(description=f'🆙 {message.author.mention} vient de monter niveau **{lvl}**.', color=0xf1c40f)
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(XP(bot))
