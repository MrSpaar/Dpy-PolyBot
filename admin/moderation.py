from discord import Member, Embed
from discord.ext import commands
from discord.utils import get

from utils.tools import has_higher_perms, parse_time
from datetime import datetime, timedelta


class Moderation(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot

    @property
    def now(self):
        return datetime.utcnow() + timedelta(hours=2)

    async def fetch_settings(self, ctx):
        settings = await self.bot.db_settings.find({'guild_id': ctx.guild.id})
        role = get(ctx.guild.roles, id=settings['mute'])
        logs = get(ctx.guild.text_channels, id=settings['logs'])

        return role, logs

    @commands.command(
        brief='@Antoine Grégoire 10m mdrr',
        usage='<membre> <durée> <raison (optionnel)>',
        description='Rendre un membre muet'
    )
    @has_higher_perms()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: Member, time, *, reason='Pas de raison'):
        role, logs = await self.fetch_settings(ctx)
        if role in member.roles:
            return await ctx.send(f"❌ {member.mention} est déjà mute")

        duration, time = parse_time(time)
        date = self.now + timedelta(seconds=duration)
        embed = (Embed(color=0xe74c3c)
                 .add_field(name='Par', value=f"```{ctx.author.display_name}```")
                 .add_field(name='Durée', value=f"```{time}```")
                 .add_field(name='Raison', value=f"```{reason}```", inline=False)
                 .set_author(name=f'{member} a été mute', icon_url=member.avatar_url))

        await ctx.send(embed=embed)
        await logs.send(embed=embed)
        await member.add_roles(role)

        try:
            await member.send(f"🔇 Tu es mute jusqu'au {date.strftime('%d/%m/%Y à %H:%M:%S')}\n⚠️ Une fois cette date dépassé, écris `!unmute` pour ne plus être mute")
        except:
            pass

        await self.bot.db_pending.insert({'type': 'mute', 'guild_id': ctx.guild.id, 'id': member.id, 'end': date})

    @commands.command(
        brief='@Antoine Grégoire',
        usage='<membre>',
        description='Redonner la parole à un membre'
    )
    async def unmute(self, ctx, member: Member = None):
        role, logs = await self.fetch_settings(ctx)
        mod = ctx.author.guild_permissions.manage_messages

        if mod and not member:
            raise commands.MissingRequiredArgument('member')

        member = member or ctx.author
        if member and role not in member.roles:
            return await ctx.send(f"❌ {member.mention} n'est pas mute")

        if not mod and member != ctx.author:
            raise commands.MissingPermissions('Manage messages')

        entry = await self.bot.db_pending.find({'type': 'mute', 'guild_id': ctx.guild.id, 'id': member.id})
        if mod not in ctx.author.roles and member == ctx.author and self.now <= entry['end']:
            return await ctx.send(f"❌ Ton mute n'est pas terminé : {entry['end'].strftime('%d/%m/%Y à %H:%M:%S')}")

        await member.remove_roles(role)
        await ctx.send(f'✅ {member.mention} a été unmute')
        await self.bot.db_pending.delete({'guild_id': ctx.guild.id, 'id': member.id})

    @commands.command(
        aliases=['prout'],
        brief='20', usage='<nombre de messages>',
        description='Supprimer plusieurs messages en même temps'
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, x: int):
        await ctx.channel.purge(limit=x+1)

    @commands.command(
        brief='@Mee6 Obselète',
        usage='<membre> <raison (optionnel)>',
        description='Exclure un membre du serveur'
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason='Pas de raison'):
        embed = (Embed(color=0xe74c3c)
                 .add_field(name='Par', value=f"```{ctx.author.display_name}```", inline=False)
                 .add_field(name='Raison', value=f"```{reason}```", inline=False)
                 .set_author(name=f'{member} a été kick', icon_url=member.avatar_url))

        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(
        brief='@Mee6 Obselète',
        usage='<membre> <raison (optionnel)>',
        description='Bannir un membre du serveur'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason='Pas de raison'):
        embed = (Embed(color=0xe74c3c)
                 .add_field(name='Par', value=f"```{ctx.author.display_name}```", inline=False)
                 .add_field(name='Raison', value=f"```{reason}```", inline=False)
                 .set_author(name=f'{member} a été ban', icon_url=member.avatar_url))

        await member.ban(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(
        brief='@Pierre Karr',
        usage='<membre> <raison (optionnel)>',
        description='Révoquer un bannissement'
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason='Pas de raison'):
        try:
            member = self.bot.get_user(user_id)
            await ctx.guild.unban(member, reason=reason)

            embed = (Embed(color=0x2ecc71)
                     .add_field(name='Par', value=f"```{ctx.author.display_name}```", inline=False)
                     .add_field(name='Raison', value=f"```{reason}```", inline=False)
                     .set_author(name=f'{member} a été unban', icon_url=member.avatar_url))

            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ L'utilisateur n'est pas banni de ce serveur")


def setup(bot):
    bot.add_cog(Moderation(bot))
