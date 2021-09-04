from discord import Member, Embed
from discord.ext import commands
from discord.utils import get


class Levels(commands.Cog, name='Niveaux', description='commands'):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_progress_bar(level, xp, n, short=False):
        needed = 5 * ((level - 1) ** 2) + (50 * (level - 1)) + 100
        progress = needed - int(5/6*level * (2*level**2 + 27*level + 91) - xp) if xp else 0
        p = int((progress/needed)*n) or 1

        if short:
            progress = f'{round(progress/1000, 1)}k' if int(progress/1000) else progress
            needed = f'{round(needed/1000, 1)}k' if int(needed/1000) else needed

        return f"{'🟩'*p}{'⬛' * (n-p)} {progress} / {needed}"

    @staticmethod
    def get_page(members, entries):
        field1, field2, field3 = '', '', ''

        for id, entry in entries.items():
            member = get(members, id=id)
            level, xp = entry['level'], entry['xp']

            bar = Levels.get_progress_bar(level + 1, xp, 5, True)
            xp = f'{round(xp / 1000, 1)}k' if int(xp / 1000) else xp

            field1 += f"**{entry['pos']}.** {member.display_name}\n"
            field2 += f'{level} ({xp})\n'
            field3 += f'{bar}\n'

        return ('Noms', field1), ('Niveau', field2), ('Progrès', field3)

    @commands.command(
        brief='@Julien Pistre',
        usage='<membre (optionnel)>',
        description='Afficher sa progression'
    )
    async def rank(self, ctx, member: Member = None):
        member = member or ctx.author
        data = await self.bot.db.members.sort({'guilds.id':ctx.guild.id}, {'guilds.$': 1}, 'guilds.xp', -1)
        data = {entry['_id']: entry['guilds'][0] | {'pos': i+1} for i, entry in enumerate(data)}

        embed = (Embed(color=0x3498db)
                 .set_author(name=f'Progression de {member.display_name}',
                             icon_url=member.avatar_url))

        xp, lvl = data[member.id]['xp'], data[member.id]['level'] + 1
        bar = self.get_progress_bar(lvl, xp, 13)

        embed.add_field(name=f"Niveau {lvl-1} • Rang {data[member.id]['pos']}", value=bar)
        await ctx.send(embed=embed)

    @commands.command(
        brief='',
        usage='',
        description='Afficher le classement du serveur'
    )
    async def levels(self, ctx):
        embed = (Embed(color=0x3498db)
                 .set_author(name='Classement du serveur', icon_url=ctx.guild.icon_url)
                 .set_footer(text='Page 1'))

        data = await self.bot.db.members.sort({'guilds.id':752921557214429316}, {'guilds.$': 1}, 'guilds.xp', -1)
        data = {entry['_id']: entry['guilds'][0] | {'pos': i+1} for i, entry in enumerate(data[:10])}
        for field in self.get_page(ctx.guild.members, data):
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

        data = await self.bot.db.members.sort({'guilds.id':752921557214429316}, {'guilds.$': 1}, 'guilds.xp', -1)

        embed, total = message.embeds[0], len(data)//10 + (len(data) % 10 > 0)
        page = (int(embed.footer.text.split()[-1]) + (-1 if emoji == '◀️' else 1)) % total or total

        a, b = (1, 10) if page == 1 else (page*10 - 9, page*10)
        data = {entry['_id']: entry['guilds'][0] | {'pos': i+a} for i, entry in enumerate(data[a-1:b])}

        for i, field in enumerate(self.get_page(member.guild.members, data)):
            embed.set_field_at(i, name=field[0], value=field[1])

        embed.set_footer(text=f'Page {page}')

        await message.edit(embed=embed)
        await reaction.remove(member)


def setup(bot):
    bot.add_cog(Levels(bot))
