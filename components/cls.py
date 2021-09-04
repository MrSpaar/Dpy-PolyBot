from discord import Game, Intents, __version__
from discord_components import ComponentsBot

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from os import environ


class Bot(ComponentsBot):
    def __init__(self, debug=False):
        load_dotenv()
        super().__init__(command_prefix='-' if debug else '!', help_command=None, case_insensitive=True,
                         activity=Game(name=f'-help') if debug else Game(name=f'!help'), intents=Intents.all())

        self.debug = debug
        self.db = Database()
        self.owner_id = 201674460393242624
        self.mention = '<@!730832334055669930>' if debug else '<@!713781013830041640>'
        self.token = environ.get('DEBUG_TOKEN') if debug else environ.get('BOT_TOKEN')

    async def on_ready(self):
        print(f'Connecté en tant que : {self.user.name} - {self.user.id}\nVersion : {__version__}\n')

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(environ['DATABASE_URL'])

        self.setup = Collection(self.client['data']['setup'])
        self.pending = Collection(self.client['data']['pending'])
        self.members = Collection(self.client['data']['members'])

        print('[INFO] Connecté à la base de données')

class Collection:
    def __init__(self, collection):
        self.collection = collection

    async def find(self, query={}, sub={}):
        if sub:
            data = await self.collection.find(query, sub).to_list(length=None)
        else:
            data = await self.collection.find(query).to_list(length=None)

        print(f'[REQ] Find : {query}')

        if len(data) > 1:
            return data
        elif data:
            return data[0]

        return

    async def update(self, query, data, upsert=False):
        await self.collection.update_one(query, data, upsert)
        print(f'[REQ] Update : {query} et {data}')

    async def insert(self, data):
        await self.collection.insert_one(data)
        print(f'[REQ] Insert : {data}')

    async def delete(self, query):
        await self.collection.delete_one(query)
        print(f'[REQ] Delete : {query}')

    async def sort(self, query, sub, field, order):
        data = self.collection.find(query, sub).sort(field, order)
        print(f'[REQ] Sort : {field}')
        return await data.to_list(length=None)