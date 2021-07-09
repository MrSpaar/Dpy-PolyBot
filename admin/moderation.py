from discord import Member, Embed
from discord.ext import commands, tasks
from discord.utils import get

from utils.tools import has_mod_role, has_higher_perms, parse_time
from datetime import datetime, timedelta
from utils.cls import Collection
from asyncio import sleep


class Moderation(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot
        self.decrement.start()

    @tasks.loop(hours=1, reconnect=True)
    async def decrement(self):
        if not self.bot.settings.next:
            await sleep(5)

        now = datetime.now()
        limit = datetime(year=now.year, month=self.bot.settings.next.month, day=self.bot.settings.next.day)
        if datetime.now() < limit:
            return

        await self.bot.settings.setv('next', datetime.now() + timedelta(days=30))
        conn = Collection(collection='users')
        data = await conn.find({'mute': {'$ne': '10m'}})

        durations = {'20m': '10m', '30m': '20m', '1h': '30m', '2h': '1h', '5h': '2h',
                     '10h': '5h', '24h': '10h', '48h': '24h', '72h': '48h'}

        for entry in data:
            await conn.update({'id': entry['id']}, {'$set': {'mute': durations[entry['mute']]}})

        print(f'[INFO] {now.strftime("%d/%m/%Y %H:%M:%S")} Paliers de mute baissés')
        conn.close()

    async def mute_member(self, entry):
        ctx, member = entry['ctx'], entry['member']
        logs = get(ctx.guild.text_channels, id=self.bot.settings.logs)
        embed = (Embed(color=0xe74c3c)
                 .add_field(name='Par', value=f"```{ctx.author.display_name}```")
                 .add_field(name='Durée', value=f"```{entry['time'][1]}```")
                 .add_field(name='Raison', value=f"```{entry['reason']}```", inline=False)
                 .set_author(name=f'{member} a été mute', icon_url=member.avatar_url))

        await ctx.send(embed=embed)
        await logs.send(embed=embed)
        await member.add_roles(entry['role'])

        date = datetime.now() + timedelta(seconds=entry['time'][0])
        try:
            await member.send(f"🔇 Tu es mute jusqu'au {date.strftime('%d/%m/%Y à %H:%M:%S')}\n⚠️ Une fois cette date dépassé, écris `!unmute` pour ne plus être mute")
        except:
            pass

        conn = Collection(collection='pending')
        entry = {'type': 'mute', 'id': member.id, 'end': date}
        await conn.insert(entry)

    @commands.command(
        brief='@Antoine Grégoire 10m mdrr',
        usage='<membre> <durée> <raison (optionnel)>',
        description='Rendre un membre muet'
    )
    @has_higher_perms()
    async def mute(self, ctx, member: Member, time, *, reason='Pas de raison'):
        role = get(ctx.guild.roles, id=self.bot.settings.mute)
        if role in member.roles:
            await ctx.send(f"❌ {member.mention} est déjà mute")
            return

        await self.mute_member({'ctx': ctx, 'role': role, 'member': member, 'reason': reason, 'time': parse_time(time)})

    @commands.command(
        brief='@Maxence Crouvezier 💤 tuorp',
        usage='<membre> <raison>',
        description='Rendre un membre muet avec durée automatique'
    )
    @has_higher_perms()
    async def automute(self, ctx, member: Member, *, reason='Pas de raison'):
        role = get(ctx.guild.roles, id=self.bot.settings.mute)
        if role in member.roles:
            await ctx.send(f"❌ {member.mention} est déjà mute")
            return

        db = Collection(collection='users')
        entry = await db.find({'id': member.id})

        duration, time = parse_time(entry['mute'])
        await self.mute_member({'ctx': ctx, 'role': role, 'member': member, 'reason': reason, 'time': parse_time(time)})

        durations = {'10m': '20m', '20m': '30m', '30m': '1h', '1h': '2h', '2h': '5h',
                     '5h': '10h', '10h': '24h', '24h': '48h', '48h': '72h'}

        await db.update({'id': member.id}, {'$set': {'mute': durations[entry['mute']]}})
        db.close()

    @commands.command(
        brief='@Antoine Grégoire',
        usage='<membre>',
        description='Redonner la parole à un membre'
    )
    async def unmute(self, ctx, member: Member = None):
        mod = get(ctx.guild.roles, id=ctx.bot.settings.mod)
        if mod in ctx.author.roles and not member:
            raise commands.MissingRequiredArgument('member')

        member = member or ctx.author
        mute = get(ctx.guild.roles, id=self.bot.settings.mute)

        if member and mute not in member.roles:
            await ctx.send(f"❌ {member.mention} n'est pas mute")
            return

        conn = Collection(collection='pending')
        if mod not in ctx.author.roles and member == ctx.author:
            entry = await conn.find({'type': 'mute', 'id': member.id})
            if entry['end'] > datetime.now():
                await ctx.send(f"❌ Ton mute n'est pas terminé : {entry['end'].strftime('%d/%m/%Y à %H:%M:%S')}")
                return

        await member.remove_roles(mute)
        await ctx.send(f'✅ {member.mention} a été unmute')

        await conn.delete({'id': member.id})
        conn.close()

    @commands.command(
        aliases=['prout'],
        brief='20', usage='<nombre de messages>',
        description='Supprimer plusieurs messages en même temps'
    )
    @has_mod_role()
    async def clear(self, ctx, x: int):
        await ctx.channel.purge(limit=x+1)

    @commands.command(
        brief='@Mee6 Obselète',
        usage='<membre> <raison (optionnel)>',
        description='Exclure un membre du serveur'
    )
    @has_higher_perms()
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
    @has_higher_perms()
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
    @has_mod_role()
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
