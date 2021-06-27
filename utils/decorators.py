from discord.ext import commands
from discord.utils import get

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
