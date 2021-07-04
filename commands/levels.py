from discord import Member, Embed
from discord.ext import commands
from discord.utils import get

from utils.cls import Collection
from pymongo import DESCENDING


class Niveaux(commands.Cog, description='commands'):
    def __init__(self, bot):
        self.bot = bot
        self.data = None

    async def cog_check(self, ctx):
        return await self.bot.is_enabled(ctx)

    @staticmethod
    def get_progress_bar(level, xp, n, short=False):
        needed = 5 * ((level - 1) ** 2) + (50 * (level - 1)) + 100
        progress = needed - int(5/6*level * (2*level**2 + 27*level + 91) - xp) if xp else 0
        p = int((progress/needed)*n) or 1

        if short:
            progress = f'{round(progress/1000, 1)}k' if int(progress/1000) else progress
            needed = f'{round(needed/1000, 1)}k' if int(needed/1000) else needed

        return f"{'🟩'*p}{'⬛' * (n-p)} {progress} / {needed} xp"

    @staticmethod
    def get_page(members, entries, start=1):
        field1, field2, field3 = '', '', ''
        for i, entry in enumerate(entries, start=start):
            member = get(members, id=entry['id'])
            level, xp = entry['level'], entry['xp']

            bar = Niveaux.get_progress_bar(level + 1, xp, 5, True)
            xp = f'{round(xp / 1000, 1)}k' if int(xp / 1000) else xp

            field1 += f'**{i}.** {member.display_name}\n'
            field2 += f'{level} ({xp} xp)\n'
            field3 += f'{bar}\n'

        return ('Noms', field1), ('Niveau', field2), ('Progrès', field3)

    @commands.command(
        brief='@Julien Pistre',
        usage='<membre (optionnel)>',
        description='Afficher sa progression'
    )
    async def rank(self, ctx, member: Member = None):
        member = member or ctx.author
        conn = Collection(collection='users')
        xp = await conn.find({'id': member.id})
        rank = (await conn.sort('xp', DESCENDING)).index(xp) + 1
        conn.close()

        embed = (Embed(color=0x3498db)
                 .set_author(name=f'Progression de {member.display_name}',
                             icon_url=member.avatar_url))

        xp, lvl = (xp['xp'], xp['level'] + 1) if xp else (0, 0)
        bar = self.get_progress_bar(lvl, xp, 13)

        embed.add_field(name=f'Niveau {lvl-1} • Rang {rank}', value=bar)
        await ctx.send(embed=embed)

    @commands.command(
        brief='',
        usage='',
        description='Afficher le classement du serveur'
    )
    async def levels(self, ctx):
        conn = Collection(database='data', collection='users')
        data = await conn.sort('xp', DESCENDING)
        conn.close()

        self.data = data
        embed = (Embed(color=0x3498db)
                 .set_author(name='Classement du serveur', icon_url=ctx.guild.icon_url)
                 .set_footer(text='Page 1'))

        for field in self.get_page(ctx.guild.members, data[:10]):
            embed.add_field(name=field[0], value=field[1])

        message = await ctx.send(embed=embed)
        for emoji in ['◀️', '▶️']:
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, member):
        if member.bot:
            return

        message, emoji = reaction.message, str(reaction.emoji)
        if not message.embeds or message.embeds[0].author.name != 'Classement du serveur':
            return

        embed, total = message.embeds[0], len(self.data)//10 + (len(self.data) % 10 > 0)
        page = (int(embed.footer.text[-1]) + (-1 if emoji == '◀️' else 1)) % total or total

        a, b = (1, 10) if page == 1 else (page*10 - 9, page*10)
        data, a = self.data[a-1:b], a or 1

        for i, field in enumerate(self.get_page(member.guild.members, data, start=a)):
            embed.set_field_at(i, name=field[0], value=field[1])

        embed.set_footer(text=f'Page {page}')

        await message.edit(embed=embed)
        await reaction.remove(member)


def setup(bot):
    bot.add_cog(Niveaux(bot))
