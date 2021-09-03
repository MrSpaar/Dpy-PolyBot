from os import listdir
from components.cls import Bot

bot = Bot(debug=True)

for directory in ['admin', 'events', 'commands']:
    for file in listdir(directory):
        if file != '__pycache__' and not (file in ['errors.py', 'logs.py'] and bot.debug):
            bot.load_extension(f'{directory}.{file[:-3]}')

bot.run(bot.token, bot=True, reconnect=True)
