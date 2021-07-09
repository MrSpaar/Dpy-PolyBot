from discord.utils import get
from discord.ext import commands
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

def has_mod_role():
    async def extended_check(ctx):
        if ctx.guild is None:
            return False

        role = get(ctx.guild.roles, id=ctx.bot.settings.mod)
        return role in ctx.author.roles
    return commands.check(extended_check)

def has_higher_perms():
    async def extended_check(ctx):
        role = get(ctx.guild.roles, id=ctx.bot.settings.mod)
        if ctx.author.top_role > ctx.message.mentions[0].top_role and role in ctx.author.roles:
            return True

        raise commands.MissingPermissions('')
    return commands.check(extended_check)
