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
            embed = (Embed(color=0xf1c40f)
                     .add_field(name='ID', value=f'```{message.id}```')
                     .add_field(name='Channel ID', value=f'```{message.channel.id}```')
                     .add_field(inline=False, name='Message', value=f'[```{message.clean_content}```]({message.to_reference().jump_url})')
                     .set_author(name=f'{payload.member.display_name} veut épingler un message', icon_url=payload.member.avatar_url))

            message = await channel.send(embed=embed)
            for emoji in ['❌', '✅']:
                await message.add_reaction(emoji)
            return

        if not message.embeds or 'veut épingler' not in message.embeds[0].author.name:
            return

        embed = message.embeds[0]

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
