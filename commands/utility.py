from discord import Embed, Member, File, PartialEmoji
from discord.ext import commands
from discord.utils import get

from inspect import getsource
from textblob import TextBlob
from os import remove


class Utilitaire(commands.Cog, description='commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['ahelp'],
        brief='utilitaire',
        usage='<argument>',
        description='Faire apparaître ce menu'
    )
    async def help(self, ctx, arg='', sub=None):
        embed = Embed(color=0x3498db, title='Aide - ')
        perm = 'admin' if ctx.invoked_with == 'ahelp' else 'commands'

        if command := get(self.bot.commands, name=arg):
            if isinstance(command, commands.Group) and sub:
                sub = command.get_command(sub)

            embed.title += command.name
            embed.description = f'{command.description}.' if not sub else sub.description

            if isinstance(command, commands.Group) and not sub:
                embed.description += f'\nLes sous-commandes disponibles :\nㅤ• ' + \
                                      '\nㅤ• '.join([cmd.name for cmd in command.walk_commands()]) + \
                                     f'\n\n Détail : `{self.bot.command_prefix}help {command.name} sous-commande`'
            elif sub:
                embed.description += f'\n\n🙋 Utilisation : `{self.bot.command_prefix}{command.name} {sub.name} {sub.usage}`\n' + \
                                     f'👉 Exemple : `{self.bot.command_prefix}{command.name} {sub.name} {sub.brief}`'
            else:
                embed.description += f'\n\n🙋 Utilisation : `{self.bot.command_prefix}{command.name} {command.usage}`\n' + \
                                     f'👉 Exemple : `{self.bot.command_prefix}{command.name} {command.brief}`'
        elif cog := [cog for cog in self.bot.cogs.values() if cog.description == perm and arg == cog.qualified_name.lower()]:
            embed.title += cog[0].qualified_name
            embed.description = '\n'.join([f'`{self.bot.command_prefix}{command.name}` : {command.description}' for command in cog[0].get_commands()])
            embed.description += f'\n\nDétail : `{self.bot.command_prefix}help commande`'
        else:
            cogs = [cog.qualified_name for cog in self.bot.cogs.values() if cog.description == perm]

            embed.title += 'Modules'
            embed.description = f'Les modules disponibles :\nㅤ• ' + '\n\ㅤ• '.join(cogs) + '\n\nDétail : `!help catégorie`'

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
        aliases=['pp', 'idp', 'pfp'],
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
        embed = (Embed(color=ctx.author.color)
                 .set_image(url=emoji.url)
                 .set_footer(text=f'<:{emoji.name}:{emoji.id}>'))
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['trad', 'translate'],
        brief='fr Hello World!',
        usage='<langue> <texte à traduire>',
        description='Traduire du texte'
    )
    async def traduire(self, ctx, lang, *, text):
        try:
            text = TextBlob(text).translate(to=lang)
            embed = Embed(color=0x3498db, description=f'📚 {text}')
        except:
            embed = Embed(color=0xe74c3c, description='❌ Traduction identique au texte initial, langue probablement invalide')

        await ctx.send(embed=embed)

    @commands.command(
        brief='',
        usage='',
        description='Envoyer le lien vers le code source du bot'
    )
    async def repo(self, ctx):
        await ctx.send('https://github.com/MrSpaar/PolyBot')

    @commands.command(
        brief='',
        usage='',
        description='Afficher le format pour envoyer du code',
    )
    async def code(self, ctx):
        await ctx.send('\`\`\`py\nTon code\n\`\`\`')

def setup(bot):
    bot.add_cog(Utilitaire(bot))
