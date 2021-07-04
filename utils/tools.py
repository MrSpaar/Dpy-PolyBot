from discord.utils import get
from discord.ext import commands
from aiohttp import ClientSession

async def get_json(link, headers=None, json=True):
    async with ClientSession() as s:
        async with s.get(link, headers=headers) as resp:
            return await resp.json() if json else await resp.text()

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
        try:
            args = ctx.message.content.split()
            member = get(ctx.guild.members, id=int(args[1].strip('<@!>')))
        except:
            return False

        return ctx.author.top_role > member.top_role and role in ctx.author.roles
    return commands.check(extended_check)
