from discord.ext import commands
from discord.utils import get

from datetime import datetime, timedelta
from unicodedata import normalize
from inspect import Parameter
from aiohttp import ClientSession

async def get_json(link, headers=None, json=True):
    async with ClientSession() as s:
        async with s.get(link, headers=headers) as resp:
            return await resp.json() if json else await resp.text()

def normalize_string(s):
    return normalize(u'NFKD', s).encode('ascii', 'ignore').decode('utf8')

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
        args = ctx.message.content.split()
        member = get(ctx.guild.members, id=int(args[1].strip('<@!>')))

        if not member:
            raise commands.MissingRequiredArgument(Parameter('member', Parameter.POSITIONAL_ONLY))

        author_perms = ctx.author.guild_permissions
        member_perms = member.guild_permissions

        if author_perms.administrator and not member_perms.administrator:
            return True
        elif author_perms.manage_guild and not member_perms.manage_guild:
            return True
        elif author_perms.ban_members and not member_perms.ban_members:
            return True
        elif author_perms.kick_members and not member_perms.kick_members:
            return True
        elif author_perms.manage_messages and not member_perms.manage_messages:
            return True
        else:
            raise commands.MissingPermissions('')

    return commands.check(extended_check)
