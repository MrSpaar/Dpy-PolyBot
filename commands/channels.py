from discord import Embed, Member, Role, PermissionOverwrite, Color
from discord.ext.commands import Greedy
from discord.ext import commands
from discord.utils import get

from typing import Union


class TempChannelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def vc_check(self, ctx):
        if not ctx.guild or not ctx.author.voice:
            embed = Embed(color=0xe74c3c, description="❌ Tu n'es connecté à un aucun channel")
            await ctx.send(embed=embed)
            return False

        entry = await ctx.bot.db.pending.find({'guild_id': ctx.guild.id, 'voc_id': ctx.author.voice.channel.id})
        if not entry:
            embed = Embed(color=0xe74c3c, description="❌ Tu n'es pas dans un channel temporaire")
            await ctx.send(embed=embed)
            return False

        owner = ctx.guild.get_member(entry['owner'])
        if ctx.author == owner:
            return entry

        embed = Embed(color=0xe74c3c, description="❌ Tu n'es pas le créateur de ce channel")
        await ctx.send(embed=embed)
        return False

    @commands.group()
    async def voc(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = Embed(color=0xe74c3c, description='❌ Sous commande inconnue : `rename` `owner`')
            await ctx.send(embed=embed)

    @voc.command(
        brief='Mdrr',
        usage='<nouveau nom>',
        description='Modifier le nom de son channel'
    )
    async def rename(self, ctx, *, name):
        entry = await self.vc_check(ctx)
        if not entry:
            return

        channel = get(ctx.guild.voice_channels, id=entry['voc_id'])
        await channel.edit(name=name)

        embed = Embed(color=0x2ecc71, description='✅ Nom modifié')
        await ctx.send(embed=embed)

    @voc.command(
        brief='@Noah Haenel',
        usage='<membre>',
        description='Définir le propriétaire du channel'
    )
    async def owner(self, ctx, member: Member):
        entry = await self.vc_check(ctx)
        if not entry:
            return

        await self.bot.db.pending.update(entry, {'$set': {'owner': member.id}})
        embed = Embed(color=0x2ecc71, description='✅ Owner modifié')
        await ctx.send(embed=embed)

    @voc.command(
        brief='@Alexandre Humbert @Noah Haenel',
        usage='<membres et/ou rôles>',
        description='Rendre le channel privé'
    )
    async def private(self, ctx, entries: Greedy[Union[Role, Member]] = None):
        entry = await self.vc_check(ctx)
        if not entry:
            return

        channel = get(ctx.guild.voice_channels, id=entry['voc_id'])
        text = get(ctx.guild.text_channels, id=entry['txt_id'])
        base = [ctx.author]

        if entries:
            entries = base+entries if isinstance(entries, list) else list(entries)+base
        else:
            entries = channel.members+base

        overwrites = {entry: PermissionOverwrite(view_channel=True, read_messages=True, connect=True,
                                                 send_messages=True, speak=True, embed_links=True,
                                                 use_external_emojis=True, stream=True, add_reactions=True,
                                                 attach_files=True, read_message_history=True) for entry in entries}
        overwrites |= {ctx.guild.default_role: PermissionOverwrite(view_channel=False),
                       ctx.me: PermissionOverwrite(view_channel=True, read_messages=True, connect=True,
                                                   send_messages=True, speak=True, manage_permissions=True,
                                                   manage_messages=True, manage_channels=True, embed_links=True,
                                                   use_external_emojis=True, stream=True, add_reactions=True,
                                                   attach_files=True, read_message_history=True)}

        await text.edit(overwrites=overwrites)
        await channel.edit(overwrites=overwrites)

        embed = Embed(color=0x2ecc71, description='✅ Permissions modifiées')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TempChannelCommands(bot))