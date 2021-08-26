from discord import Member, Embed, Permissions, PermissionOverwrite, Color
from discord.ext import commands
from discord.utils import get
from textblob import blob

from components.tools import has_higher_perms, now
from datetime import timedelta
from time import mktime

class Moderation(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_settings(self, guild):
        settings = await self.bot.db.settings.find({'guild_id': guild.id})
        role = get(guild.roles, id=settings['mute'])
        logs = get(guild.text_channels, id=settings['logs'])

        if not role:
            role = await guild.create_role(name='Muted', color=0xa6aaab, permissions=Permissions.none())
            await self.bot.db.settings.update({'guild_id': guild.id}, {'$set': {'mute': role.id}})

            for channel in guild.text_channels:
                overwrite = channel.overwrites | {role:  PermissionOverwrite(add_reactions=False, send_messages=False)}
                await channel.edit(overwrites=overwrite)

        return role, logs

    @commands.command(
        brief='@Antoine Grégoire 10m mdrr',
        usage='<membre> <durée> <raison (optionnel)>',
        description='Rendre un membre muet'
    )
    #@has_higher_perms()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: Member, time=None):
        role, _ = await self.fetch_settings(ctx.guild)
        if role in member.roles:
            embed = Embed(color=0xe74c3c, description=f'❌ {member.mention} est déjà mute')
            return await ctx.send(embed=embed)

        try:
            units = {"s": [1, 'secondes'], "m": [60, 'minutes'], "h": [3600, 'heures']}
            date = now() + timedelta(seconds=(int(time[:-1])*units[time[-1]][0]))
            time = f"{time[:-1]} {units[time[-1]][1]}"
        except:
            date = now() + timedelta(days=1000)
            time = 'indéfiniment'

        try:
            await member.add_roles(role)
            embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été mute {time}')
            await ctx.send(embed=embed)
            await self.bot.db.pending.insert({'type': 'mute', 'guild_id': ctx.guild.id, 'id': member.id, 'end': date})
        except:
            embed = Embed(color=0xe74c3c, description='❌ La cible a plus de permissions que moi')

        try:
            date = now() + timedelta(days=1000)
            unix = int(mktime(date.timetuple()))
            embed = Embed(color=0x3498db, description=f'🔇 Tu as été mute sur **{ctx.guild.name}**.\nTu pourras écrire `!cancel` <t:{unix}:R> pour te unmute.')

            await member.send(embed=embed)
        except:
            pass

    @commands.command(
        brief='',
        usage='',
        description="Se unmute une fois qu'un mute est terminé"
    )
    async def cancel(self, ctx):
        entries = await self.bot.db.pending.find({'type': 'mute', 'id': ctx.author.id})
        if not entries:
            embed = Embed(color=0xe74c3c, description="❌ Tu n'es mute sur aucun de mes serveurs")
            return await ctx.send(embed=embed)

        entries = [entries] if not isinstance(entries, list) else entries
        for entry in entries:
            guild = self.bot.get_guild(entry['guild_id'])

            if now() <= entry['end']:
                continue

            member = guild.get_member(entry['id'])
            role, _ = await self.fetch_settings(guild)

            await member.remove_roles(role)
            await self.bot.db.pending.delete(entry)

            embed = Embed(color=0x2ecc71, description=f'✅ Tu as été unmute de **{guild.name}**')
            await ctx.send(embed=embed)

    @commands.command(
        brief='@Antoine Grégoire',
        usage='<membre>',
        description='Redonner la parole à un membre'
    )
    @has_higher_perms()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: Member):
        role, _ = await self.fetch_settings(ctx.guild)
        if role not in member.roles:
            return await ctx.send(f"❌ {member.mention} n'est pas mute")

        await member.remove_roles(role)
        await self.bot.db.pending.delete({'guild_id': ctx.guild.id, 'id': member.id})

        embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été unmute')
        await ctx.send(embed=embed)

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
        embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été kick')

        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @commands.command(
        brief='@Mee6 Obselète',
        usage='<membre> <raison (optionnel)>',
        description='Bannir un membre du serveur'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason='Pas de raison'):
        embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été ban')

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

            embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été unban')

            await ctx.send(embed=embed)
        except:
            embed = Embed(color=0xe74c3c, description="❌ L'utilisateur n'est pas banni de ce serveur")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
