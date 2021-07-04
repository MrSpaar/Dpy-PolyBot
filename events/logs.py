from discord import Embed, Member, AuditLogAction
from discord.ext import commands
from discord.utils import get

from datetime import datetime, timedelta
from utils.cls import Collection


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = Collection(collection='users')
        if not conn.find({'id': member.id}) and not member.bot:
            await conn.insert({'id': member.id, 'xp': 0, 'level': 0, 'mute': '10m'})
        conn.close()

        channel = get(member.guild.text_channels, id=self.bot.settings.logs)
        embed = Embed(color=0x2ecc71, description=f'**:inbox_tray: {member.mention} a rejoint le serveur !**')
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        entry = await member.guild.audit_logs(limit=1).flatten()
        if entry[0].action == AuditLogAction.ban:
            embed = (Embed(title=':man_judge: Membre ban', color=0xe74c3c)
                     .add_field(name='Par', value=f'```{entry[0].user}```', inline=False)
                     .add_field(name='Cible', value=f'```{entry[0].target}```', inline=False)
                     .add_field(name='Raison', value=f'```{entry[0].reason}```', inline=False))
        elif entry[0].action == AuditLogAction.kick:
            embed = (Embed(title=':man_judge: Membre kick', color=0xe74c3c)
                     .add_field(name='Par', value=f'```{entry[0].user}```', inline=False)
                     .add_field(name='Cible', value=f'```{entry[0].target}```', inline=False)
                     .add_field(name='Raison', value=f'```{entry[0].reason}```', inline=False))
        else:
            embed = Embed(color=0xe74c3c, description=f'**:outbox_tray: {member.display_name} ({member}) a quitté le serveur**')

        channel = get(member.guild.text_channels, id=self.bot.settings.logs)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        entry = await guild.audit_logs(limit=1).flatten()
        embed = Embed(title=':man_judge: Membre unban', color=0xc27c0e,
                      description=f"{entry[0].user.mention} a unban {user}\n**Raison:** {entry[0].reason}")

        channel = get(guild.text_channels, id=self.bot.settings.logs)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        entry = (await after.guild.audit_logs(limit=1).flatten())[0]
        embed = (Embed(title="🗒️ Modification de profil", color=0x3498db)
                 .add_field(name='Cible', value=f'```{before.display_name}```')
                 .add_field(name='Par', value=f'```{entry.user.display_name}```'))

        if before.display_name != after.display_name:
            value = f"```{before.display_name} → {after.display_name}```"
            embed.add_field(name="Pseudo:", value=value, inline=False)
        elif before.roles != after.roles:
            try:
                role = list(filter(lambda r: r not in before.roles, after.roles))[0].name
                state = 1
            except:
                role = list(filter(lambda r: r not in after.roles, before.roles))[0].name
                state = 0
            value = f'```Role "{role}"' + (' ajouté' if state else ' enlevé')+'```'
            embed.add_field(name="Roles", value=value, inline=False)
        else:
            return

        channel = get(before.guild.text_channels, id=self.bot.settings.logs)
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
                 .add_field(name='Message de', value=f'```{message.author.display_name}```', inline=False)
                 .add_field(name='Dans', value=f'```#{message.channel}```'))

        if message.content:
            embed.add_field(name='Contenu', value=f'```{message.clean_content}```', inline=False)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        channel = get(message.guild.text_channels, id=self.bot.settings.logs)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        embed = (Embed(color=0x3498db)
                 .set_author(name='Modification Discord', icon_url=before.avatar_url))

        if before.name != after.name and before.discriminator != after.discriminator:
            embed.add_field(name='Pseudo', value=f'```{before.name} → {after.name}```', inline=False)
            embed.add_field(name='Discriminant', value=f'```{before.discriminator} → {after.discriminator}```', inline=False)
        if before.name != after.name and before.discriminator == after.discriminator:
            embed.add_field(name='Cible', value=f'```{after}```', inline=False)
            embed.add_field(name='Avant', value=f'```{before.name}```')
            embed.add_field(name='Après', value=f'```{after.name}```')
        elif before.discriminator != after.discriminator and before.name == after.name:
            embed.add_field(name='Cible', value=f'```{after}```', inline=False)
            embed.add_field(name='Avant', value=f'```{before.discriminator}```')
            embed.add_field(name='Après', value=f'```{after.discriminator}```')
        else:
            return

        guild = self.bot.get_guild(752921557214429316)
        channel = get(guild.text_channels, id=self.bot.settings.logs)

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

        channel = get(invite.guild.text_channels, id=self.bot.settings.logs)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.command.name not in ['mute', 'automute'] or not await ctx.command.can_run(ctx):
            return

        cmd = ctx.command.name
        args = ctx.message.content[len(f'{self.bot.command_prefix}{ctx.invoked_with}')+1:].split(' ')

        member = ctx.message.mentions[0]
        title = f"Membre {'muté' if cmd in ['mute', 'automute'] else 'warn'}"

        embed = (Embed(color=0xe74c3c)
                 .add_field(name='Cible', value=f"```{member.display_name}```")
                 .add_field(name='Par', value=f"```{ctx.author.display_name}```")
                 .set_author(name=title, icon_url=member.avatar_url))

        if cmd == 'mute':
            embed.set_author(name='Membre muté', icon_url=member.avatar_url)
            embed.add_field(name='Durée', value=f"```{args[1]}```")
            embed.add_field(name='Raison', value=f"```{' '.join(args[2:]) if len(args) > 2 else 'Pas de raison'}```", inline=False)
        else:
            embed.set_author(name='Membre automuté', icon_url=member.avatar_url)
            embed.add_field(name='Raison', value=f"```{' '.join(args[1:]) if args[1:] else 'Pas de raison'}```", inline=False)

        channel = get(ctx.guild.text_channels, id=self.bot.settings.logs)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))
