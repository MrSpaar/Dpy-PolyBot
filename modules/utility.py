from discord import Role, CategoryChannel, VoiceChannel, Embed
from discord_components import Button, ButtonStyle, Select, SelectOption
from discord.ext import commands
from discord.utils import get

from typing import Union


class Utility(commands.Cog, name='Utilitaire', description='admin'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief='@CM 1 @CM 2',
        usage='<rôles ou id catégories>',
        description='Cloner des rôles ou des catégories'
    )
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def clone(self, ctx, to_clone: commands.Greedy[Union[Role, CategoryChannel]]):
        for obj in to_clone:
            if isinstance(obj, CategoryChannel):
                clone = await obj.clone()
                for channel in obj.channels:
                    if isinstance(channel, VoiceChannel):
                        await clone.create_voice_channel(name=channel.name, overwrites=channel.overwrites)
                    else:
                        await clone.create_text_channel(name=channel.name, overwrites=channel.overwrites)

                await ctx.send(f'✅ Catégorie `{obj}` clonée')
            elif isinstance(obj, Role):
                await ctx.guild.create_role(name=obj.name, color=obj.color, hoist=obj.hoist,
                                            permissions=obj.permissions, mentionable=obj.mentionable)

                await ctx.send(f'Rôle `@{obj}` cloné')

    @commands.group(
        brief='boutons @CM 1 @CM 2 Groupes de CM',
        usage='<sous commande> <sous arguments>',
        description='Commandes liées aux menus de rôles'
    )
    @commands.has_permissions(manage_roles=True)
    async def menu(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            embed = Embed(color=0xe74c3c, description='❌ Sous commande inconnue : `boutons` `liste`')
            await ctx.send(embed=embed)

    @menu.command(
        name='boutons',
        brief='@CM 1 @CM 2 Groupes de CM',
        usage='<rôles> <titre>',
        description='Faire un menu de rôles avec des boutons'
    )
    @commands.has_permissions(manage_roles=True)
    async def buttons(self, ctx, roles: commands.Greedy[Role], *, title):
        buttons = [[Button(label=role.name, style=ButtonStyle.green, custom_id=role.id) for role in roles]]
        await ctx.send(f'Menu de rôles - {title}', components=buttons)

    @menu.command(
        brief='🥫 @Kouizinier 🎮 @Soirées jeux',
        usage='<emojis et rôles> <titre>',
        description='Faire un menu de rôles avec des boutons incluant des emojis'
    )
    async def emoji(self, ctx, entries: commands.Greedy[Union[Role, str]]):
        buttons = [[Button(label=role.name, style=ButtonStyle.green, custom_id=role.id, emoji=emoji) for emoji, role in zip(entries[::2], entries[1::2])]]
        await ctx.send(f'Menu de rôles', components=buttons)

    @menu.command(
        name='liste',
        brief='@CM 1 @CM 2 Choisis ton CM',
        usage='<rôles> <titre>',
        description='Faire un menu de rôles avec une liste déroulante'
    )
    @commands.has_permissions(manage_roles=True)
    async def dropdown(self, ctx, roles: commands.Greedy[Role], *, title):
        select = [Select(placeholder=title, 
                        options=[
                            SelectOption(label=role.name, value=role.id) for role in roles
                        ])]
        await ctx.send('Menu de rôles', components=select)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if 'Menu de rôles' not in interaction.message.content:
            return

        role = get(interaction.guild.roles, id=int(interaction.component.custom_id))
        await interaction.user.add_roles(role)
        await interaction.respond(content=f'✅ Rôle {role.mention} ajouté')

    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        if 'Menu de rôles' not in interaction.message.content:
            return

        roles = [get(interaction.guild.roles, id=int(option.value)) for option in interaction.component.options]
        if common := [role for role in roles if role in interaction.user.roles]:
            return await interaction.respond(content=f'❌ Tu as déjà un des rôles ({common[0].mention})')

        role = get(interaction.guild.roles, id=int(interaction.values[0]))
        await interaction.user.add_roles(role)
        await interaction.respond(content=f'✅ Rôle {role.mention} ajouté')


def setup(bot):
    bot.add_cog(Utility(bot))
