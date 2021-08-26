from discord import Embed, Member, member
from discord.ext import commands
from discord.utils import get

from components.tools import now
from datetime import timedelta
from time import mktime


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, embed):
        settings = await self.bot.db.settings.find({'guild_id': guild.id})
        logs = get(guild.text_channels, id=settings['logs'])

        if logs:
            await logs.send(embed=embed)
        return settings

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not await self.bot.db.users.find({'guild_id': member.guild.id, 'id': member.id}) and not member.bot:
            await self.bot.db.users.insert({'guild_id': member.guild.id, 'id': member.id, 'xp': 0, 'level': 0})

        embed = Embed(color=0x2ecc71, description=f':inbox_tray: {member.mention} a rejoint le serveur !')
        settings = await self.send_log(member.guild, embed)

        for role_id in settings['new']:
            role = get(member.guild.roles, id=role_id)
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        await self.bot.db.users.delete({'guild_id': member.guild.id, 'id': member.id})

        embed = Embed(color=0xe74c3c, description=f':outbox_tray: {member.display_name} ({member}) a quitté le serveur')
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await guild.audit_logs(limit=1).flatten()
        embed = Embed(color=0xc27c0e, description=f"👨‍⚖️ {entry[0].user} a unban {user}\n❔ Raison : {entry[0].reason or 'Pas de raison'}")

        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        entry = (await after.guild.audit_logs(limit=1).flatten())[0]
        member = get(before.guild.members, id=entry.user.id)
        embed = Embed(color=0x3498db)

        if before.display_name != after.display_name:
            embed.description = f"📝 {member.mention} a changé de surnom (`{before.display_name} → {after.display_name}`)"
        elif before.roles != after.roles:
            new = list(filter(lambda r: r not in before.roles, after.roles))
            removed = list(filter(lambda r: r not in after.roles, before.roles))
            role, = new if new else removed

            embed.description = f"📝 {member.mention} à {'ajouté' if new else 'retiré'} {role} à {before.mention}"
        else:
            return

        await self.send_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.embeds or message.author.bot or message.channel.id == 840555556707237928 or len(message.content) == 1 or \
           (len(message.content) in [5, 6, 7] and message.content.count(',') == 2):
            return

        flags = [
            (now(utc=True)-message.created_at).total_seconds() <= 20 and message.mentions and message.content,
            message.content and not message.attachments,
            message.content or message.attachments
        ]

        infos = [
            {'emoji': '<:ping:768097026402942976>', 'color': 0xe74c3c},
            {'emoji': '🗑️', 'color': 0x979c9f},
            {'emoji': '🗑️', 'color': 0xf1c40f}
        ]

        entry = [infos[i] for i, flag in enumerate(flags) if flag][0]

        embed = Embed(color=entry['color'], description=f'{entry["emoji"]} {message.author.mention} a supprimé un message dans {message.channel.mention}:')

        if message.content:
            embed.description += f'\n\n> {message.content}'
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await self.send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        guild = self.bot.get_guild(752921557214429316)
        if before not in guild.members:
            return

        embed = Embed(color=0x3498db)

        if before.name != after.name and before.discriminator != after.discriminator:
            embed.description = f'📝 {before.mention} a changé de Gamer Tag (`{before} → {after}`)'
        if before.name != after.name and before.discriminator == after.discriminator:
            embed.description = f'📝 {before.mention} a changé de pseudo (`{before.name} → {after.name}`)'
        elif before.discriminator != after.discriminator and before.name == after.name:
            embed.description = f'📝 {before.mention} a changé de discriminant (`{before.discriminator} → {after.discriminator}`)'
        else:
            return

        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        uses = f'{invite.max_uses} fois' if invite.max_uses else "à l'infini"
        expire = f'<t:{int(mktime((now() + timedelta(seconds=invite.max_age)).timetuple()))}:R>' if invite.max_age else 'jamais'

        embed = Embed(color=0x3498db, description=f'✉️ {invite.inviter.mention} a créé une invitation qui expire {expire}, utilisable {uses} : {invite.url}')
        await self.send_log(invite.guild, embed)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        print(f'[INFO] {now().strftime("%d/%m/%Y %H:%M:%S")} Commande exécutée sur {ctx.guild.name}')
        print(f'Par {ctx.author} : {ctx.message.clean_content}')


def setup(bot):
    bot.add_cog(Logs(bot))
