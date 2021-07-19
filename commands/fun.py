from discord import Member
from discord.ext import commands

from games.minesweeper import Minesweeper
from games.hangman import Hangman
from games.dchess import Chess
from random import randint, choice


class Fun(commands.Cog, description='commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['chess'],
        brief='@Noah Conrard', usage='<membre>',
        description="Jouer aux échecs contre quelqu'un"
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def echecs(self, ctx, opponent: Member):
        if opponent.bot or opponent == ctx.author:
            return await ctx.send('Tu ne peux pas jouer contre un bot ou contre toi-même')
        
        game = Chess(self.bot, ctx, opponent)
        if not await game.start():
            return

        await game.play()

    @commands.command(
        aliases=['hangman'],
        brief='',
        usage='',
        description='Jouer au pendu'
    )
    async def pendu(self, ctx):
        await Hangman(self.bot, ctx).start()

    @commands.command(
        aliases=['minesweeper'],
        brief='',
        usage='',
        description='Jouer au démineur'
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def demineur(self, ctx):
        await Minesweeper(self.bot, ctx).start()

    @commands.command(
        aliases=['pof', 'hot'],
        brief='pile',
        usage='<pile ou face>',
        description='Jouer au pile ou face contre le bot'
    )
    async def toss(self, ctx, arg):
        result = choice(['Pile', 'Face'])

        if arg.title() not in ['Pile', 'Face']:
            desc = '❌ Tu dois entrer "pile" ou "face"!'
        elif arg.title() in result:
            desc = f'🪙 {result} ! Tu as gagné.'
        else:
            desc = f'🪙 {result} ! Tu as perdu.'

        await ctx.send(desc)

    @commands.command(
        brief='2d6+5d20+20',
        usage='<texte>',
        description='Faire une lancer de dés'
    )
    async def roll(self, ctx, dices):
        content = dices.split('+')
        rolls = [int(content.pop(i))
                 for i in range(len(content)) if content[i].isdigit()]

        for elem in content:
            n, faces = elem.split('d') if elem.split('d')[
                0] != '' else (1, elem[1:])
            rolls += [randint(1, int(faces)) for _ in range(int(n))]

        rolls_str = ' + '.join([str(n) for n in rolls])
        await ctx.send(f"**🎲 Résultat du lancé :** {rolls_str} = **{sum(rolls)}**")


def setup(bot):
    bot.add_cog(Fun(bot))
