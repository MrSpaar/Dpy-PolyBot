from discord import Embed
from discord.ext import commands


class Pin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if str(payload.emoji) == '📌':
            channel = self.bot.get_channel(755477957849382962)
            embed = (Embed(color=0xf1c40f, description=f'💬 [{message.clean_content}]({message.to_reference().jump_url})')
                     .set_author(name=f'{payload.member.display_name} veut épingler un message', icon_url=payload.member.avatar_url))

            message = await channel.send(embed=embed)
            for emoji in ['❌', '✅']:
                await message.add_reaction(emoji)
            return

        if not message.embeds:
            return

        embed = message.embeds[0]
        if not embed.author or not embed.author.name or 'veut épingler' not in embed.author.name:
            return

        if str(payload.emoji) == '❌':
            embed.color = 0xe74c3c
            embed.set_author(name='Message non épinglé', icon_url=payload.member.avatar_url)

            await message.edit(embed=embed)
        elif str(payload.emoji) == '✅':
            channel = self.bot.get_channel(int(embed.fields[1].value.strip('`')))
            message_pin = await channel.fetch_message(int(embed.fields[0].value.strip('`')))

            embed.color = 0x2ecc71
            embed.set_author(name='Message épinglé', icon_url=payload.member.avatar_url)

            await message_pin.pin()
            await message.edit(embed=embed)

        await message.clear_reactions()

def setup(bot):
    bot.add_cog(Pin(bot))
