from discord.ext import commands
from discord.utils import get
from utils.db import Collection


class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        db = Collection(collection='pending')

        mute = get(member.guild.roles, id=self.bot.settings.mute)
        name = f'Salon de {member.display_name}'
        temp = await db.find({'name': name})

        if after.channel and 'Créer' in after.channel.name and mute not in member.roles and not member.bot and not temp:
            if cat := after.channel.category:
                overwrites = after.channel.overwrites
                text = await member.guild.create_text_channel(name=f'Salon-de-{member.display_name}', category=cat, overwrites=overwrites)
                channel = await member.guild.create_voice_channel(name=name, category=cat, overwrites=overwrites)
                try:
                    await member.move_to(channel)
                    await db.insert({'name': name, 'txt_id': text.id})
                except:
                    await channel.delete()
                    await text.delete()
            return

        if before.channel:
            chan = await db.find({'name': before.channel.name})
            if chan and ((len(before.channel.members) <= 1 and member.guild.me in before.channel.members) or not len(before.channel.members)):
                await before.channel.delete()
                channel = get(member.guild.text_channels, id=chan['txt_id'])
                await channel.delete()
                await db.delete({'name': before.channel.name})

        db.close()


def setup(bot):
    bot.add_cog(Channels(bot))
