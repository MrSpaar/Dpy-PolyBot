from discord import Embed, Member, File, PartialEmoji
from discord.ext import commands
from discord.utils import get

from inspect import getsource
from textblob import TextBlob
from os import remove


class Utilitaire(commands.Cog, description='commands'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_enabled(ctx)

    @commands.command(
        aliases=['ahelp'],
        brief='utilitaire',
        usage='<catégorie ou commande (optionnel)>',
        description='Faire apparaître ce menu'
    )
    async def help(self, ctx, command=''):
        mod = get(ctx.guild.roles, id=self.bot.settings.mod)
        mod = mod in ctx.author.roles or ctx.author.guild_permissions.administrator
        command = get(self.bot.commands, name=command)

        if (ctx.invoked_with == 'ahelp' and not mod) or \
           (not mod and command and command.cog.description == 'admin'):
            raise commands.MissingPermissions('')

        if command:
            embed = (Embed(color=0x3498db)
                     .add_field(name='Description', value=f'```{command.description}```')
                     .add_field(name='Utilisation',
                                value=f'```{self.bot.command_prefix}{command.name} {command.usage}```', inline=False)
                     .add_field(name='Exemple', value=f'```{self.bot.command_prefix}{command.name} {command.brief}```')
                     .set_author(name=f"Menu d'aide • {self.bot.command_prefix}{command}"))

            if command.aliases:
                embed.add_field(name='Alias', value=f'```{", ".join(command.aliases)}```')
        else:
            embed = (Embed(color=0x3498db)
                     .set_author(name="Menu d'aide", icon_url=ctx.guild.icon_url)
                     .set_footer(text=f"{self.bot.command_prefix}help <commande> pour plus d'informations"))

            cat = 'admin' if ctx.invoked_with == 'ahelp' else 'commands'
            for cog in [cog for cog in self.bot.cogs.values() if cog.description == cat]:
                cmds = [command.name for command in cog.get_commands()]
                embed.add_field(name=cog.qualified_name, value=f"```{', '.join(cmds)}```", inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        aliases=['poll'],
        brief="Êtes-vous d'accord ? | Oui | Non",
        usage='<question> | <choix 1> | <choix 2> | ...',
        description='Faire un sondage (9 choix au maximum)'
    )
    async def sondage(self, ctx, *, args):
        items = [arg.strip() for arg in args.split('|')]
        question = items[0]
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        embed = (Embed(title=f'>> {question[0].upper() + question[1:]}', color=0x3498db)
                 .set_author(name=f'Sondage de {ctx.author.display_name}', icon_url=ctx.author.avatar_url))

        await ctx.message.delete()

        for i in range(1, len(items)):
            embed.add_field(name=f"{reactions[i-1]} Option n°{i}", value=f'```{items[i]}```', inline=False)

        message = await ctx.channel.send(embed=embed)

        for i in range(len(items[1:])):
            await message.add_reaction(reactions[i])

    @commands.command(
        brief='play',
        usage='<commande>',
        description="Afficher le code source d'une commande"
    )
    async def source(self, ctx, command):
        source = str(getsource(self.bot.get_command(command).callback))

        if len(source) > 2000:
            with open(f'{command}.py', 'w', encoding='UTF-8') as file:
                file.write(source)
            await ctx.send(file=File(f'{command}.py', f'{command}.py'))
            remove(f'{command}.py')
        else:
            return await ctx.send("```py\n" + source.replace('`', '\`') + "\n```")

    @commands.command(
        aliases=['pp', 'idp'],
        brief='@[!] Polybot',
        usage='<mention>',
        description="Afficher l'image de profil d'un membre"
    )
    async def pdp(self, ctx, member: Member = None):
        member = member or ctx.author
        await ctx.send(embed=(Embed(color=member.color)).set_image(url=member.avatar_url))

    @commands.command(
        brief=':pepeoa:',
        usage='<emoji custom>',
        description="Afficher l'image d'un emoji"
    )
    async def emoji(self, ctx, emoji: PartialEmoji):
        await ctx.send(embed=(Embed(color=ctx.author.color)).set_image(url=emoji.url))

    @commands.command(
        aliases=['trad'],
        brief='fr Hello World!',
        usage='<langue> <texte à traduire>',
        description='Traduire du texte'
    )
    async def traduire(self, ctx, lang, *, text):
        try:
            text = TextBlob(text).translate(to=lang)
            await ctx.send(f'📚 **Traduction :**\n```{text}```')
        except:
            await ctx.send('❌ Texte traduit identique au texte initial, langue probablement invalide')


def setup(bot):
    bot.add_cog(Utilitaire(bot))
