from discord import Role, CategoryChannel, VoiceChannel, Embed
from discord_components import Button, ButtonStyle, Select, SelectOption
from discord.ext import commands

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

    @commands.group()
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


def setup(bot):
    bot.add_cog(Utility(bot))
