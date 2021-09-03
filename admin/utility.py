from discord import Role, CategoryChannel, VoiceChannel, Embed, Color
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

    @commands.command(
        brief='@CM 1 @CM 2',
        usage='<rôles>',
        description='Faire un menu de rôles'
    )
    @commands.has_permissions(manage_roles=True)
    async def menu(self, ctx, roles: commands.Greedy[Role], *, title):
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🇦', '🇧']
        embed = (Embed(color=0x3498db, description='')
                 .set_author(name=f'Menu - {title}', icon_url=ctx.guild.icon_url))

        for emoji, role in  zip(emojis, roles):
            embed.description += f'{emoji} {role.mention}\n'

        message = await ctx.send(embed=embed)
        for i in range(len(roles)):
            await message.add_reaction(emojis[i])


def setup(bot):
    bot.add_cog(Utility(bot))
