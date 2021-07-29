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
        if (message.author.id == 689154823941390507 and 'mdrr' in message.content.lower()) or not message.guild or message.channel.id == 840555556707237928:
            return

        bucket = self.cd.get_bucket(message)
        if bucket.update_rate_limit() or message.author.bot or not message.channel.category or message.channel.id == 853630887794311178:
            return

        member = await self.bot.db_users.find({'guild_id': message.guild.id, 'id': message.author.id})
        if not member:
            return

        xp, lvl = member['xp'] + (randint(15, 25)), member['level'] + 1
        next_lvl = 5 / 6 * lvl * (2 * lvl ** 2 + 27 * lvl + 91)

        await self.bot.db_users.update({'guild_id': message.guild.id, 'id': message.author.id},
                                       {'$set': {'xp': int(xp), 'level': lvl if xp >= next_lvl else lvl - 1}})

        if xp >= next_lvl:
            settings = await self.bot.db_settings.find({'guild_id': message.guild.id})
            channel = get(message.guild.text_channels, id=settings['channel']) or message.channel
            embed = Embed(description=f'🆙 Tu viens de monter niveau **{lvl}**.', color=0xf1c40f)
            await channel.send(message.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(XP(bot))
