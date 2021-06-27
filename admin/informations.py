from discord import Embed, Status, Member, Role, TextChannel
from discord.ext import commands

from datetime import datetime
from utils.decorators import has_mod_role


class Informations(commands.Cog, description='admin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='',
        usage='',
        description='Afficher des informations à propos du serveur'
    )
    @has_mod_role()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        channels = f'{len(guild.text_channels)} textuels et {len(guild.voice_channels)} vocaux'

        since = str(datetime.now() - guild.created_at).replace('days', 'jours').split(', ')
        since = f"{since[0]} et {since[1].split(':')[0]} heures"
        creation = guild.created_at.strftime('%d/%m/%Y')

        bots = [member for member in guild.members if member.bot]
        online = len([1 for member in guild.members if member.status != Status.offline])

        embed = (Embed(description=guild.description if guild.description else '', color=0x546e7a)
                 .add_field(name='Membres', value=f'```{guild.member_count - len(bots)} ({online} en ligne)```')
                 .add_field(name='Bots', value=f'```{len(bots)}```')
                 .add_field(name='Création', value=f"```{creation} ({since})```", inline=False)
                 .add_field(name='Owner', value=f'```{guild.owner.display_name}```')
                 .add_field(name='Région', value=f'```{str(guild.region).title()}```')
                 .add_field(name='ID', value=f'```{guild.id}```', inline=False)
                 .add_field(name='Roles', value=f'```{len(guild.roles)}```')
                 .add_field(name='Channels', value=f'```{channels}```')
                 .set_author(name=f'Informations de serveur', icon_url=guild.icon_url))

        await ctx.send(embed=embed)

    @commands.command(
        brief='@Julien Pistre',
        usage='<membre>',
        description="Afficher des informations à propos du serveur d'un membre"
    )
    @has_mod_role()
    async def userinfo(self, ctx, member: Member = None):
        member = member or ctx.author
        flags = [str(f)[10:].replace('_', ' ').title() for f in member.public_flags.all()]
        flags = ', '.join(flags) if flags else 'Pas de flags'

        status = {
            'online': 'En ligne',
            'offline': 'Hors ligne',
            'invisible': 'Invisible',
            'idle': 'Absent',
            'dnd': 'Ne pas déranger'
        }
        activity = member.activity.name if member.activity and member.activity.name else "Rien"

        since = member.joined_at.strftime('%d/%m/%Y')
        creation = member.created_at.strftime("%d/%m/%Y")
        joined = str(datetime.now() - member.joined_at).replace('days', 'jours').split(', ')
        joined = f"{joined[0]} et {joined[1].split(':')[0]} heures"

        embed = (Embed(color=0x1abc9c)
                 .add_field(name='Pseudo', value=f'```{member}```')
                 .add_field(name='Surnom', value=f'```{member.display_name}```')
                 .add_field(name='Membre depuis', value=f"```{since} ({joined})```", inline=False)
                 .add_field(name='Création du compte', value=f'```{creation}```')
                 .add_field(name='Status', value=f'```{status[str(member.status)]}```')
                 .add_field(name='Activité en cours', value=f"""```{activity}```""")
                 .add_field(name='ID', value=f'```{member.id}```', inline=False)
                 .add_field(name='Role principal', value=f'```{member.top_role}```')
                 .add_field(name='Flags', value=f"```{flags}```")
                 .set_author(name=f"Informations de membre", icon_url=member.avatar_url))

        if member.premium_since:
            since = member.premium_since.strftime("%d/%m/%Y")
            embed.add_field(name='📈 Booste depuis', value=since, inline=True)
            embed.add_field(name='\u200b', value='\u200b')

        await ctx.send(embed=embed)

    @commands.command(
        brief='@Modo',
        usage='<role>',
        description="Afficher des informations à propos du serveur d'un rôle"
    )
    @has_mod_role()
    async def roleinfo(self, ctx, role: Role):
        since = role.created_at.strftime("%d/%m/%Y")
        perms = role.permissions
        perms = {
            'Administrateur': perms.administrator,
            'Gérer le serveur': perms.manage_guild,
            'Modifier les permissions': perms.manage_permissions,
            'Modifier les channels': perms.manage_channels,
            'Modifier les rôles': perms.manage_roles,
            'Voir les logs': perms.view_audit_log,
            'Bannir des membres': perms.ban_members,
            'Expulser des membres': perms.kick_members,
            'Gérer les messages': perms.manage_messages,
            'Gérer les emojis': perms.manage_emojis,
            'Gérer les pseudos': perms.manage_nicknames,
            'Muter les autres': perms.mute_members,
            'Bouger les autres': perms.move_members,
            'Ajouter des réactions': perms.add_reactions,
            'Changer de nom': perms.change_nickname,
            'Mentionner everyone': perms.mention_everyone,
            'Envoyer des TTS': perms.send_tts_messages,
            'Envoyer des messages': perms.send_messages,
            'Lire les historiques': perms.read_message_history,
            'Lire les messages': perms.read_messages,
            'Parler': perms.speak,
            'Streamer': perms.stream,
            'Se connecter': perms.connect,
        }

        result = ''
        for key, value in perms.items():
            result += f'✅ {key}\n' if value else f'❌ {key}\n'

        embed = (Embed(color=role.color)
                 .add_field(name='Nom', value=f'```{role}```')
                 .add_field(name='ID', value=f'```{role.id}```')
                 .add_field(name='Permissions', value=f'```{result}```', inline=False)
                 .add_field(name='Membres', value=f'```{len(role.members)}```')
                 .add_field(name='Position', value=f'```{role.position}```')
                 .add_field(name='Création', value=f'```{since}```')
                 .set_author(name=f"Informations de rôle", icon_url=ctx.guild.icon_url))
        
        await ctx.send(embed=embed)

    @commands.command(
        brief='#-general',
        usage='<channel>',
        description="Afficher des informations à propos d'un channel"
    )
    @has_mod_role()
    async def channelinfo(self, ctx, channel: TextChannel = None):
        channel = channel or ctx.channel
        category = channel.category if channel.category else "Pas de catégorie"

        bots = len([1 for member in channel.members if member.bot])
        members = len(channel.members) - bots

        embed = (Embed(color=0x3498db)
                 .add_field(name='Nom', value=f'```#{channel}```')
                 .add_field(name='ID', value=f'```{channel.id}```')
                 .add_field(name='Membres', value=f'```{members} membres et {bots} bots```', inline=False)
                 .add_field(name='Position', value=f'```{channel.position}```')
                 .add_field(name='Catégorie', value=f'```{category}```')
                 .set_author(name=f"Informations de channel", icon_url=ctx.guild.icon_url))
        
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['lj'],
        brief='5',
        usage="<nombre d'entrées>",
        description='Afficher les nouveaux membres les plus récents'
    )
    @has_mod_role()
    async def lastjoins(self, ctx, x: int = 10):
        members = filter(lambda m: not m.bot, sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True))
        members = [f'`{member.name}` : {str(member.joined_at)[:10]} ({member.id})'.replace('-', '/') for member in members]
        string = '\n'.join(members[:x])

        embed = (Embed(description=string, color=0x2ecc71)
                 .set_author(name=f'Derniers {x} nouveaux membres', icon_url=ctx.guild.icon_url))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Informations(bot))
