from discord import Embed
from discord.ext import commands
from discord.utils import get

from utils.cls import Collection
from random import randint


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 689154823941390507 and 'mdrr' in message.content.lower() or not message.guild:
            return

        bucket = self.cd.get_bucket(message)
        if bucket.update_rate_limit() or message.author.bot or not message.channel.category or message.channel.id == 853630887794311178:
            return

        conn1 = Collection(collection='users')
        coeff = await conn1.find({'id': message.channel.category.id})
        conn1.close()

        if not coeff:
            return

        conn2 = Collection(collection='channels')
        member, coeff = await conn2.find({'id': message.author.id}), coeff['value']

        xp, lvl = member['xp'] + (randint(15, 25)) * coeff, member['level'] + 1
        next_lvl = 5 / 6 * lvl * (2 * lvl ** 2 + 27 * lvl + 91)

        await conn2.update({'id': message.author.id},
                           {'$set': {'xp': int(xp), 'level': lvl if xp >= next_lvl else lvl - 1}})
        conn2.close()

        if xp >= next_lvl:
            channel = get(message.guild.text_channels, id=self.bot.settings.announce)
            embed = Embed(description=f'🆙 Tu viens de monter niveau **{lvl}**.', color=0xf1c40f)
            await channel.send(message.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(XP(bot))
