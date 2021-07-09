from discord import Embed, Color

from random import sample


class Minesweeper:
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.message = None
        self.embed = None
        self.end = False

        self.emotes = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        self.mine, self.flag, self.blank = '🇲', '🚩', '🟦'

        self.checks = (
            lambda i, m: -1 < i - 10 < 100 and (self.sol[i - 10] == self.mine or m),
            lambda i, m: -1 < i + 10 < 100 and (self.sol[i + 10] == self.mine or m),
            lambda i, m: -1 < i + 1 < 100 and (self.sol[i + 1] == self.mine or m) and (i + 1) % 10,
            lambda i, m: -1 < i - 9 < 100 and (self.sol[i - 9] == self.mine or m) and (i + 1) % 10,
            lambda i, m: -1 < i + 11 < 100 and (self.sol[i + 11] == self.mine or m) and (i + 1) % 10,
            lambda i, m: -1 < i - 1 < 100 and (self.sol[i - 1] == self.mine or m) and i % 10,
            lambda i, m: -1 < i + 9 < 100 and (self.sol[i + 9] == self.mine or m) and i % 10,
            lambda i, m: -1 < i - 11 < 100 and (self.sol[i - 11] == self.mine or m) and i % 10,
        )

        self.sol = sample(self.blank*75 + self.mine*25, 100)
        self._cur = list(self.blank*100)

        for i, elem in enumerate(self.sol):
            if elem != self.mine:
                self.sol[i] = self.emotes[len([1 for c in self.checks if c(i, False)])]

    @property
    def grid(self):
        temp = f"⬛⬛{''.join(self.emotes[1:])}\n{'⬛'*12}\n"
        for i in range(0, 100, 10):
            temp += f"{self.emotes[1:][i//10]}⬛{'​'.join(self._cur[i:i+10])}\n"
        return temp

    @grid.setter
    def grid(self, i):
        if self.sol[i] == self.mine:
            self.end = True

        self._cur[i], temp = self.sol[i], []
        if self._cur[i] == self.emotes[0]:
            self.reveal_near(i)

    def reveal_near(self, i, lastest=[]):
        for x, c in zip((-10, 10, 1, -9, 11, -1, 9, -11), self.checks):
            if c(i, True):
                self._cur[i+x] = self.sol[i+x]
                if self.sol[i+x] == self.emotes[0] and i+x not in lastest:
                    lastest.append(i + x)
                    self.reveal_near(i+x, lastest)

    async def edit_embed(self, description=None, color=None, name=None):
        self.embed.color = color or self.embed.color
        self.embed.description = description or self.embed.description
        self.embed.set_author(name=name or 'Partie de démineur', icon_url=self.ctx.author.avatar_url)

        await self.message.edit(embed=self.embed)

    async def start(self):
        self.embed = (Embed(color=Color.random(), description=self.grid)
                      .set_author(name='Partie de démineur', icon_url=self.ctx.author.avatar_url))
        self.message = await self.ctx.send(embed=self.embed)

        for emoji in [self.flag, '⛏️', '🗑️']:
            await self.message.add_reaction(emoji)

        await self.loop()

    async def loop(self):
        while True:
            reaction, member = await self.bot.wait_for('reaction_add', check=lambda r, m: m == self.ctx.author)
            if str(reaction) == '🗑️':
                await self.edit_embed(color=0xe74c3c, name='Partie abandonnée')
                return

            pos = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
            await pos.delete()
            await reaction.remove(member)

            try:
                a, b = [int(x.strip()) for x in pos.content.split('/')]
                if -1 < a < 11 and -1 < b < 11:
                    pos = (a - 1) * 10 + b - 1
                    reaction = str(reaction.emoji)
                    break
            except:
                pass

        if reaction == self.flag:
            self._cur[pos] = self.flag
        elif reaction == '⛏️':
            self.grid = pos

        if self.blank not in self.grid and self.grid.count(self.flag) == 25:
            await self.edit_embed(color=0xf1c40f, name='Partie gagnée !', description=self.grid)
        elif not self.end:
            await self.edit_embed(description=self.grid)
            await self.loop()
        else:
            desc = '\n'.join(['​'.join(self.sol[i:i+10]) for i in range(0, 100, 10)])
            await self.edit_embed(color=0xe74c3c, name='Partie perdue !', description=desc)
