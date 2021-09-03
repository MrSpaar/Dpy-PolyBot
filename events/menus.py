from discord import message
from discord.ext import commands
from discord.utils import get


class RoleMenus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        guild = get(self.bot.guilds, id=payload.guild_id)
        channel = get(guild.text_channels, id=payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = get(message.reactions, emoji=str(payload.emoji))

        if not message.embeds:
            return

        embed = message.embeds[0]
        if not embed.author or 'Menu - ' not in embed.author.name:
            return

        roles = {line.split()[0]: get(guild.roles, id=int(line.split()[-1].strip('<@&>'))) for line in embed.description.split('\n')}
        if any([role in payload.member.roles for role in roles.values()]):
            await reaction.remove(payload.member)
            return

        print('1')
        


def setup(bot):
    bot.add_cog(RoleMenus(bot))
