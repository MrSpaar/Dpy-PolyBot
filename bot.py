from discord import Game, Intents
from discord.ext import commands

from os import listdir
from utils.cls import Bot

bot = Bot(intents=Intents.all(), case_insensitive=True,
          help_command=None, activity=Game(name=f'!help'), debug=False)

for directory in ['admin', 'events', 'commands']:
    for file in listdir(directory):
        if file == '__pycache__' or (file == 'errors.py' and bot.debug):
            continue

        bot.load_extension(f'{directory}.{file[:-3]}')

@bot.command()
@commands.is_owner()
async def restart(ctx):
    for directory in ['admin', 'events', 'commands']:
        for file in listdir(directory):
            if file == '__pycache__' or (file == 'errors.py' and bot.debug):
                continue

            bot.load_extension(f'{directory}.{file[:-3]}')
    await ctx.send('Tous les modules ont été relancé')

bot.run(bot.token, bot=True, reconnect=True)
