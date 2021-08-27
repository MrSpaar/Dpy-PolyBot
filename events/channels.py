from discord.ext import commands
from discord.utils import get


class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        entry = await self.bot.db.pending.find({'guild_id': member.guild.id, 'id': member.id})

        if after.channel and 'Créer' in after.channel.name and not member.bot and not entry:
            if cat := after.channel.category:
                text = await member.guild.create_text_channel(name=f'Salon-de-{member.display_name}', category=cat, overwrites=after.channel.overwrites)
                channel = await member.guild.create_voice_channel(name=f'Salon de {member.display_name}', category=cat, overwrites=after.channel.overwrites)

                try:
                    await member.move_to(channel)
                    await self.bot.db.pending.insert({'guild_id': member.guild.id, 'id': member.id, 'voc_id': channel.id, 'txt_id': text.id})
                except:
                    await channel.delete()
                    await text.delete()
            return

        if before.channel:
            entry = await self.bot.db.pending.find({'guild_id': member.guild.id, 'voc_id': before.channel.id})
            if entry and ((len(before.channel.members) <= 1 and member.guild.me in before.channel.members) or not len(before.channel.members)):
                await before.channel.delete()
                channel = get(member.guild.text_channels, id=entry['txt_id'])
                await channel.delete()
                await self.bot.db.pending.delete(entry)


def setup(bot):
    bot.add_cog(Channels(bot))
