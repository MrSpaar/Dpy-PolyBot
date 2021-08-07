from discord import Member, Embed, Permissions, PermissionOverwrite, CategoryChannel, VoiceChannel
from discord.ext import commands
from discord.utils import get

from utils.tools import has_higher_perms, parse_time, now
from datetime import timedelta

class Moderation(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_settings(self, guild):
        settings = await self.bot.db_settings.find({'guild_id': guild.id})
        role = get(guild.roles, id=settings['mute'])
        logs = get(guild.text_channels, id=settings['logs'])

        if not role:
            role = await guild.create_role(name='Muted', color=0xa6aaab, permissions=Permissions.none())
            await self.bot.db_settings.update({'guild_id': guild.id}, {'$set': {'mute': role.id}})

            for channel in guild.text_channels:
                overwrite = channel.overwrites | {role:  PermissionOverwrite(add_reactions=False, send_messages=False)}
                await channel.edit(overwrites=overwrite)

        return role, logs

    @commands.command(
        brief='@Antoine Grégoire 10m mdrr',
        usage='<membre> <durée> <raison (optionnel)>',
        description='Rendre un membre muet'
    )
    @has_higher_perms()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: Member, time=None, *, reason=None):
        role, logs = await self.fetch_settings(ctx.guild)
        if role in member.roles:
            return await ctx.send(f"❌ {member.mention} est déjà mute")

        try:
            duration, time = parse_time(time)
            date = now() + timedelta(seconds=duration)
        except:
            reason = f'{time} {reason if reason else ""}' if time else 'Pas de raison'
            time = 'Indéfiniment'
            date = now() + timedelta(days=1000)

        embed = (Embed(color=0xe74c3c)
                 .add_field(name='Par', value=f"```{ctx.author.display_name}```")
                 .add_field(name='Durée', value=f"```{time}```")
                 .add_field(name='Raison', value=f"```{reason or 'Pas de raison'}```", inline=False)
                 .set_author(name=f'{member} a été mute', icon_url=member.avatar_url))

        await member.add_roles(role)
        await ctx.send(embed=embed)
        if logs:
            await logs.send(embed=embed)

        try:
            await member.send(f"🔇 Tu es mute jusqu'au {date.strftime('%d/%m/%Y à %H:%M:%S')} sur **{ctx.guild.name}**" +
                              "\n⚠️ Une fois cette date dépassé, écris `!cancel` ici pour ne plus être mute")
        except:
            pass

        await self.bot.db_pending.insert({'type': 'mute', 'guild_id': ctx.guild.id, 'id': member.id, 'end': date})

    @commands.command(
        brief='',
        usage='',
        description="Se unmute une fois qu'un mute est terminé"
    )
    async def cancel(self, ctx):
        entries = await self.bot.db_pending.find({'type': 'mute', 'id': ctx.author.id})
        if not entries:
            return await ctx.send("❌ Tu n'es mute sur aucun de mes serveurs")

        entries = [entries] if not isinstance(entries, list) else entries
        for entry in entries:
            guild = self.bot.get_guild(entry['guild_id'])

            if now() <= entry['end']:
                await ctx.send(f"❌ Mute non terminé sur **{guild.name}** ({entry['end'].strftime('%d/%m/%Y à %H:%M:%S')})")
                continue

            member = guild.get_member(entry['id'])
            role, _ = await self.fetch_settings(guild)

            await member.remove_roles(role)
            await ctx.send(f'✅ Tu as été unmute de **{guild.name}**')
            await self.bot.db_pending.delete(entry)

    @commands.command(
        brief='@Antoine Grégoire',
        usage='<membre>',
        description='Redonner la parole à un membre'
    )
    @has_higher_perms()
    @commands.has_permissions(manage_permissions=True)
    async def unmute(self, ctx, member: Member):
        role, _ = await self.fetch_settings(ctx.guild)
        if role not in member.roles:
            return await ctx.send(f"❌ {member.mention} n'est pas mute")

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

    @commands.command()
    async def clone(self, ctx, cat: CategoryChannel):
        clone = await cat.clone()
        for channel in cat.channels:
            if isinstance(channel, VoiceChannel):
                await clone.create_voice_channel(name=channel.name, overwrites=channel.overwrites)
            else:
                await clone.create_text_channel(name=channel.name, overwrites=channel.overwrites)


def setup(bot):
    bot.add_cog(Moderation(bot))
