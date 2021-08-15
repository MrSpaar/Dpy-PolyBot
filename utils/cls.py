from discord import __version__
from discord.ext import commands

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from os import environ


class Bot(commands.Bot):
    def __init__(self, debug=False, **kwargs):
        super().__init__(command_prefix='-' if debug else '!', **kwargs)
        load_dotenv()

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
        self.source = self.client['data']

        self.settings = Collection(self.source, 'settings')
        self.users = Collection(self.source, 'users')
        self.pending = Collection(self.source, 'pending')

        print('[INFO] Connecté à la base de données')

class Collection:
    def __init__(self, source, collection):
        self.conn = source[collection]

    async def find(self, query=None):
        query = query or {}
        data = await self.conn.find(query).to_list(length=None)

        if len(data) > 1:
            return data
        elif data:
            return data[0]

        print(f'[REQ] Find : {query}')
        return

    async def update(self, query, data, upsert=False):
        await self.conn.update_one(query, data, upsert)
        print(f'[REQ] Update : {query} et {data}')

    async def insert(self, data):
        await self.conn.insert_one(data)
        print(f'[REQ] Insert : {data}')

    async def delete(self, query):
        await self.conn.delete_one(query)
        print(f'[REQ] Delete : {query}')

    async def sort(self, query, field, order):
        data = self.conn.find(query).sort(field, order)
        print(f'[REQ] Sort : {field}')
        return await data.to_list(length=None)
