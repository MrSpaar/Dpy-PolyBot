from discord.ext import commands

from aiohttp import ClientSession
from os import environ


class OpenAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith(message.guild.me.mention):
            return

        question = message.content.strip(message.guild.me.mention).strip()
        data = '{"prompt": "%s", "max_tokens": 100, "temperature": 0.1}' % question

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {environ["OPENAI_TOKEN"]}',
        }

        async with message.channel.typing():
            async with ClientSession() as s:
                async with s.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers, data=data) as resp:
                    data = await resp.json()
                    try:
                        await message.channel.send(data['choices'][0]['text'].split('\n\n')[1].strip('—-'))
                    except:
                        await message.channel.send("J'ai pas compris :(")


def setup(bot):
    bot.add_cog(OpenAI(bot))
