from discord import Embed, Member, Role, PermissionOverwrite, Color
from discord.ext.commands import Greedy
from discord.ext import commands
from discord.utils import get

from typing import Union


class TempChannelCommands(commands.Cog, name='Vocaux', description='commands'):
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

    @commands.group(
        brief='owner @Alexandre Humber',
        usage='<sous commande> <sous arguments>',
        description='Commandes liées aux channels temporaires'
    )
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
        base = channel.members if ctx.author in channel.members else [ctx.author] + channel.members

        if entries:
            entries = base+entries if isinstance(entries, list) else list(entries)+base

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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        entry = await self.bot.db.pending.find({'guild_id': member.guild.id, 'owner': member.id})

        if after.channel and 'Créer' in after.channel.name and not member.bot and not entry:
            if cat := after.channel.category:
                text = await member.guild.create_text_channel(name=f'Salon-de-{member.display_name}', category=cat, overwrites=after.channel.overwrites)
                channel = await member.guild.create_voice_channel(name=f'Salon de {member.display_name}', category=cat, overwrites=after.channel.overwrites)

                try:
                    await member.move_to(channel)
                    await self.bot.db.pending.insert({'guild_id': member.guild.id, 'owner': member.id, 'voc_id': channel.id, 'txt_id': text.id})
                except:
                    await channel.delete()
                    await text.delete()
            return

        if before.channel:
            entry = await self.bot.db.pending.find({'guild_id': member.guild.id, 'voc_id': before.channel.id})
            if entry and ((len(before.channel.members) <= 1 and member.guild.me in before.channel.members) or not len(before.channel.members)):
                await before.channel.delete()
                channel = get(member.guild.text_channels, id=entry['txt_id'])
                await channel.delete()
                await self.bot.db.pending.delete(entry)


def setup(bot):
    bot.add_cog(TempChannelCommands(bot))
