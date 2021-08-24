from discord import Game, Intents
from discord.ext import commands

from os import listdir
from components.cls import Bot

bot = Bot(intents=Intents.all(), case_insensitive=True,
          help_command=None, activity=Game(name=f'!help'), debug=True)

for directory in ['admin', 'events', 'commands']:
    for file in listdir(directory):
        if file not in ['__pycache__', 'logs.py', 'errors.py']:
            bot.load_extension(f'{directory}.{file[:-3]}')

@bot.command()
@commands.is_owner()
async def reload(ctx):
    for directory in ['admin', 'events', 'commands']:
        for file in listdir(directory):
            if file not in ['__pycache__', 'logs.py', 'errors.py']:
                bot.reload_extension(f'{directory}.{file[:-3]}')
    await ctx.send('Tous les modules ont été relancé')

bot.run(bot.token, bot=True, reconnect=True)
