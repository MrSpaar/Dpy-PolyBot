from discord import Game, Intents, __version__
from discord.ext import commands
from discord.utils import get

from os import listdir, environ
from utils.db import Settings
from dotenv import load_dotenv


class Bot(commands.Bot):
    def __init__(self, debug=False, **kwargs):
        super().__init__(command_prefix='-' if debug else '!', **kwargs)
        load_dotenv()

        self.debug = debug
        self.settings = Settings()
        self.token = environ.get('DEBUG_TOKEN') if debug else environ.get('BOT_TOKEN')

    async def on_ready(self):
        self.settings = await self.settings.start()
        print(f'\nConnecté en tant que : {self.user.name} - {self.user.id}\nVersion : {__version__}\n')
        print(f'Le bot est prêt !')

    async def is_enabled(self, ctx):
        if not ctx.guild:
            return True

        role = get(ctx.guild.roles, id=self.settings.mod)
        return ctx.channel.id in self.settings.channels or ctx.command.name == 'sondage' or role in ctx.author.roles


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
            if file != '__pycache__':
                try:
                    bot.reload_extension(f'{directory}.{file[:-3]}')
                except:
                    pass
    await ctx.send('Tous les modules ont été relancé')

bot.run(bot.token, bot=True, reconnect=True)
