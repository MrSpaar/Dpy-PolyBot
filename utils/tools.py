from discord.ext import commands

from datetime import datetime, timedelta
from inspect import Parameter
from aiohttp import ClientSession

async def get_json(link, headers=None, json=True):
    async with ClientSession() as s:
        async with s.get(link, headers=headers) as resp:
            return await resp.json() if json else await resp.text()

def parse_time(time):
    units = {"s": [1, 'secondes'], "m": [60, 'minutes'], "h": [3600, 'heures']}
    duration = int(time[:-1]) * units[time[-1]][0]
    time = f"{time[:-1]} {units[time[-1]][1]}"

    return duration, time

def now(utc=False):
    if utc:
        return datetime.utcnow()
    return datetime.utcnow() + timedelta(hours=2)

def has_higher_perms():
    async def extended_check(ctx):
        if not ctx.message.mentions:
            raise commands.MissingRequiredArgument(Parameter('member', Parameter.POSITIONAL_ONLY))

        if ctx.author.top_role > ctx.message.mentions[0].top_role:
            return True

        raise commands.MissingPermissions('')
    return commands.check(extended_check)
