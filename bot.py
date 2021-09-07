from os import listdir
from components.cls import Bot

bot = Bot(debug=False)

for file in listdir('modules'):
    if file != '__pycache__' and not (file in ['errors.py', 'logs.py'] and bot.debug):
        bot.load_extension(f'modules.{file[:-3]}')

bot.run(bot.token, bot=True, reconnect=True)
