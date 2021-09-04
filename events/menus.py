from discord.ext import commands
from discord.utils import get


class RoleMenus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if 'Menu de rôles' not in interaction.message.content:
            return

        buttons = interaction.message.components[0].components
        roles = [get(interaction.guild.roles, id=int(button.custom_id)) for button in buttons]

        if common := [role for role in roles if role in interaction.user.roles]:
            return await interaction.respond(content=f'❌ Tu as déjà un des rôles ({common[0].mention})')

        role = get(interaction.guild.roles, id=int(interaction.component.custom_id))
        await interaction.user.add_roles(role)
        await interaction.respond(content=f'✅ Rôle {role.mention} ajouté')

    @commands.Cog.listener()
    async def on_select_option(interaction):
        if 'Menu de rôles' not in interaction.message.content:
            return

        roles = [get(interaction.guild.roles, id=int(option.value)) for option in interaction.component.options]
        if common := [role for role in roles if role in interaction.user.roles]:
            return await interaction.respond(content=f'❌ Tu as déjà un des rôles ({common[0].mention})')

        role = get(interaction.guild.roles, id=int(interaction.values[0]))
        await interaction.user.add_roles(role)
        await interaction.respond(content=f'✅ Rôle {role.mention} ajouté')

def setup(bot):
    bot.add_cog(RoleMenus(bot))
