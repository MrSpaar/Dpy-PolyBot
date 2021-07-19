from discord.ext import commands
from discord.utils import get


class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        name = f'Salon de {member.display_name}'
        temp = await self.bot.db_pending.find({'guild_id': member.guild.id, 'name': name})

        if after.channel and 'Créer' in after.channel.name and not member.bot and not temp:
            if cat := after.channel.category:
                overwrites = after.channel.overwrites
                text = await member.guild.create_text_channel(name=f'Salon-de-{member.display_name}', category=cat, overwrites=overwrites)
                channel = await member.guild.create_voice_channel(name=name, category=cat, overwrites=overwrites)
                try:
                    await member.move_to(channel)
                    await self.bot.db_pending.insert({'type': 'channel', 'guild_id': member.guild.id, 'name': name, 'txt_id': text.id})
                except:
                    await channel.delete()
                    await text.delete()
            return

        if before.channel:
            chan = await self.bot.db_pending.find({'guild_id': member.guild.id, 'name': before.channel.name})
            if chan and ((len(before.channel.members) <= 1 and member.guild.me in before.channel.members) or not len(before.channel.members)):
                await before.channel.delete()
                channel = get(member.guild.text_channels, id=chan['txt_id'])
                await channel.delete()
                await self.bot.db_pending.delete({'guild_id': member.guild.id, 'name': before.channel.name})


def setup(bot):
    bot.add_cog(Channels(bot))
