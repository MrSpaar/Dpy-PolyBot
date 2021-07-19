from discord.ext import commands

from utils.tools import get_json


class Maths(commands.Cog, name='Mathématiques', description='commands'):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def base_conv(k, b, n):
        def to_base(num, b, numerals='0123456789abcdefghijklmnopqrstuvwxyxABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

        return to_base(int(str(k), b), n)

    @commands.command(
        brief='16 f',
        usage='<base> <nombre>',
        description="Convertir en base n depuis n'importe quelle base (uniquement des nombres, base 52 maximum)"
    )
    async def base(self, ctx, from_base: int, to_base: int, num: str):
        if from_base > 62 or to_base > 52:
            return await ctx.send('❌ Base trop grande (base 52 maximum)')

        conv = self.base_conv(num, from_base, to_base)
        await ctx.send(f'**⚙️ Convertion base {from_base} en base {to_base} :** `{conv}`')

    @commands.command(
        aliases=['bin', 'binary'],
        brief='prout',
        usage='<texte>',
        description='Convertir du texte en binaire'
    )
    async def binaire(self, ctx, *, arg):
        try:
            conv = [bin(int(arg))[2:]]
        except:
            conv = [bin(s)[2:] for s in bytearray(arg, 'utf-8')]

        await ctx.send(f'**⚙️ Conversion binaire :** `{"".join(conv)}`')

    @commands.command(
        aliases=['hex', 'hexa'],
        brief='16',
        usage='<texte>',
        description='Convertir du texte en hexadécimal'
    )
    async def hexadecimal(self, ctx, *, arg):
        await ctx.send(f'**⚙️ Conversion hexadécimale :** `{arg.encode().hex()}`')

    @commands.command(
        aliases=['compute'],
        brief='3*log(50)',
        usage='<expression>',
        description='Faire des calculs'
    )
    async def calcul(self, ctx, *, expr):
        query = expr.replace('+', '%2B').replace('x', '*')
        result = await get_json(f"https://api.mathjs.org/v4/?expr={query}", json=False)
        await ctx.send(f':pager: `{expr}` = `{result}`')


def setup(bot):
    bot.add_cog(Maths(bot))
