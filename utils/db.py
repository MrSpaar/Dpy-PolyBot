from motor.motor_asyncio import AsyncIOMotorClient
from os import environ


class Collection:
    def __init__(self, client=None, database='data', collection=None):
        self.client = client or AsyncIOMotorClient(environ['DATABASE_URL'])
        self.collection = self.client[database][collection]

    async def find(self, query=None):
        query = query or {}
        data = await self.collection.find(query).to_list(length=None)

        if len(data) > 1:
            return data
        elif data:
            return data[0]
        return

    async def update(self, query, data, upsert=False):
        await self.collection.update_one(query, data, upsert)

    async def update_many(self, query, data, upsert=False):
        await self.collection.update_many(query, data, upsert)

    async def insert(self, data):
        await self.collection.insert_one(data)

    async def insert_many(self, data):
        await self.collection.insert_many(data)

    async def delete(self, query):
        await self.collection.delete_one(query)

    async def sort(self, field, order):
        data = self.collection.find().sort(field, order)
        return await data.to_list(length=None)

    def close(self):
        self.client.close()


class Database:
    def __init__(self, connections):
        self.client = AsyncIOMotorClient(environ['DATABASE_URL'])
        self.xp = None
        self.coeff = None

        for key, value in connections.items():
            setattr(self, key, Collection(self.client, value[0], value[1]))

    def close(self):
        self.client.close()


class Settings:
    def __init__(self):
        self.collection = Collection(collection='settings')
        self.mute = None
        self.mod = None
        self.logs = None
        self.next = None
        self.channels = None
        self.channel = None

    async def start(self):
        settings = await self.collection.find()
        self.collection.close()

        for key, value in settings.items():
            setattr(self, f'{key}', value)

        return self

    async def setv(self, key, value):
        setattr(self, key, value)
        await self.collection.update({}, {'$set': {key: value}})
        self.collection.close()
