from discord import Embed, Member, AuditLogAction
from discord.ext import commands
from discord.utils import get

from datetime import datetime, timedelta


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_logs(self, guild):
        settings = await self.bot.db_settings.find({'guild_id': guild.id})
        logs = get(guild.text_channels, id=settings['logs'])
        return logs

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.db_settings.insert({'guild_id': guild.id, 'mute': None, 'logs': None, 'channel': None})
        await self.bot.db_users.collection.insert_many([{'id': member.id, 'level': 0, 'xp': 0} for member in guild.members])

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.db_settings.delete({'guild_id': guild.id})
        await self.bot.db_users.delete({'guild_id': guild.id})

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.bot.db_users.find({'guild_id': member.guild.id, 'id': member.id}) and not member.bot:
            await self.bot.db_users.insert({'guild_id': member.guild.id, 'id': member.id, 'xp': 0, 'level': 0})

        embed = Embed(color=0x2ecc71, description=f'**:inbox_tray: {member.mention} a rejoint le serveur !**')

        channel = await self.get_logs(member.guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        entry = await member.guild.audit_logs(limit=1).flatten()
        await self.bot.db_users.delete({'guild_id': member.guild.id, 'id': member.id})

        if entry[0].action == AuditLogAction.ban:
            embed = (Embed(title=':man_judge: Membre ban', color=0xe74c3c)
                     .add_field(name='Par', value=f'```{entry[0].user}```')
                     .add_field(name='Cible', value=f'```{entry[0].target}```')
                     .add_field(name='Raison', value=f'```{entry[0].reason}```', inline=False))
        elif entry[0].action == AuditLogAction.kick:
            embed = (Embed(title=':man_judge: Membre kick', color=0xe74c3c)
                     .add_field(name='Par', value=f'```{entry[0].user}```')
                     .add_field(name='Cible', value=f'```{entry[0].target}```')
                     .add_field(name='Raison', value=f'```{entry[0].reason}```', inline=False))
        else:
            embed = Embed(color=0xe74c3c, description=f'**:outbox_tray: {member.display_name} ({member}) a quitté le serveur**')

        channel = await self.get_logs(member.guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await guild.audit_logs(limit=1).flatten()
        embed = Embed(title=':man_judge: Membre unban', color=0xc27c0e,
                      description=f"{entry[0].user.mention} a unban {user}\nRaison: {entry[0].reason}")

        channel = await self.get_logs(guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        entry = (await after.guild.audit_logs(limit=1).flatten())[0]
        embed = (Embed(title="🗒️ Modification de profil", color=0x3498db)
                 .add_field(name='Cible', value=f'```{before.display_name}```')
                 .add_field(name='Par', value=f'```{entry.user.display_name}```'))

        if before.display_name != after.display_name:
            value = f"```{before.display_name} → {after.display_name}```"
            embed.add_field(name="Pseudo:", value=value)
        elif before.roles != after.roles:
            try:
                role = list(filter(lambda r: r not in before.roles, after.roles))[0].name
                state = 1
            except:
                role = list(filter(lambda r: r not in after.roles, before.roles))[0].name
                state = 0
            value = f'```Role "{role}"' + (' ajouté' if state else ' enlevé')+'```'
            embed.add_field(name="Roles", value=value)
        else:
            return

        channel = await self.get_logs(before.guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.embeds or message.author.bot or message.channel.id == 840555556707237928 or len(message.content) == 1:
            return

        flags = [datetime.now().second - message.created_at.second <= 20 and message.mentions and message.content and message.attachments,
                 datetime.now().second - message.created_at.second <= 20 and message.mentions and message.content,
                 message.content and not message.attachments,
                 message.content and message.attachments,
                 message.attachments]

        infos = [{'title': '<:ping:768097026402942976> Ghost ping + Image supprimée', 'color': 0xe74c3c},
                 {'title': '<:ping:768097026402942976> Ghost ping', 'color': 0xe74c3c},
                 {'title': '🗑️ Message supprimé', 'color': 0x979c9f},
                 {'title': '🗑️ Message + Image supprimés', 'color': 0xf1c40f},
                 {'title': '🗑️ Image supprimée', 'color': 0xf1c40f}]

        entry = [infos[i] for i, flag in enumerate(flags) if flag][0]

        embed = (Embed(title=entry['title'], color=entry['color'])
                 .add_field(name='Message de', value=f'```{message.author.display_name}```')
                 .add_field(name='Dans', value=f'```#{message.channel}```'))

        if message.content:
            inline = True if len(message.clean_content) < 31 else False
            embed.add_field(name='Contenu', value=f'```{message.clean_content}```', inline=inline)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        channel = await self.get_logs(message.guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        embed = (Embed(color=0x3498db)
                 .set_author(name='Modification Discord', icon_url=before.avatar_url))

        if before.name != after.name and before.discriminator != after.discriminator:
            embed.add_field(name='Pseudo', value=f'```{before.name} → {after.name}```')
            embed.add_field(name='Discriminant', value=f'```{before.discriminator} → {after.discriminator}```', inline=False)
        if before.name != after.name and before.discriminator == after.discriminator:
            embed.add_field(name='Cible', value=f'```{after}```')
            embed.add_field(name='Avant', value=f'```{before.name} → {after.name}```')
        elif before.discriminator != after.discriminator and before.name == after.name:
            embed.add_field(name='Cible', value=f'```{after}```', inline=False)
            embed.add_field(name='Avant', value=f'```{before.discriminator} → {after.discriminator}```')
        else:
            return

        guild = self.bot.get_guild(752921557214429316)
        channel = await self.get_logs(guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        uses = invite.max_uses or 'Infini'
        if not invite.max_age:
            expire = 'Jamais'
        else:
            expire = (datetime.now() + timedelta(seconds=invite.max_age)).strftime('%d/%m/%Y à %H:%M:%S')

        embed = (Embed(color=0x3498db)
                 .add_field(name='Créée par', value=f'```{invite.inviter}```')
                 .add_field(name='Channel', value=f'```#{invite.channel}```')
                 .add_field(name='Lien', value=f'```{invite.url}```', inline=False)
                 .add_field(name='Expiration', value=f'```{expire}```')
                 .add_field(name='Utilisations max', value=f'```{uses}```')
                 .set_author(name='Invitation créée', icon_url=invite.inviter.avatar_url))

        channel = await self.get_logs(invite.guild)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        now = datetime.now()
        print(f'[INFO] {now.strftime("%d/%m/%Y %H:%M:%S")} Commande exécutée')
        print(f'Par {ctx.author} : {ctx.message.clean_content}')


def setup(bot):
    bot.add_cog(Logs(bot))
