from discord import Embed, Color

from random import choice


class Hangman:
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.message = None
        self.embed = None
        self.end = False
        self.word = choice([ligne.strip() for ligne in open('wordlist.txt')])
        self.words = [list(self.word), ['-'] * len(self.word)]
        self.lives, self.errors = 5, []

    async def parse(self, s):
        if s in ['quit', 'quitter', 'leave', 'stop']:
            await self.ctx.send(f"Partie terminée. Le mot était `{self.word}`")
            self.end = True
            return
        elif s in self.errors:
            await self.ctx.send('Tu as déjà entré cette lettre.', delete_after=3)
            return
        elif s not in self.word:
            self.lives -= 1
            self.errors.append(s)
            await self.edit()
            return

        self.words[1] = [s if s == self.words[0][i] else c for i, c in enumerate(self.words[1])]

        if s == self.word or self.words[1] == self.words[0]:
            await self.ctx.send('Bravo ! Tu as gagné :)')
            self.words[1] = self.words[0]

        await self.edit()

    async def edit(self):
        value1 = f"```{''.join(self.words[1])}```"
        value2 = f"```{', '.join(self.errors)}```" if self.errors else '```\u200b```'

        self.embed.set_field_at(0, name='Mot', value=value1, inline=False)
        self.embed.set_field_at(1, name='Erreurs', value=value2, inline=False)
        self.embed.set_footer(text=f'Vies : {self.lives}')

        await self.message.edit(embed=self.embed)

    async def play(self):
        while not self.end:
            entry = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
            await self.parse(entry.content)
            await entry.delete()

            if not self.lives:
                await self.ctx.send(f'Perdu ! Le mot était `{self.word}`')
                self.end = True

    async def start(self):
        self.embed = (Embed(title='Partie de pendu', color=Color.random())
                      .add_field(name='Mot', value=f"```{''.join(self.words[1])}```", inline=False)
                      .add_field(name='Erreurs', value='```\u200b```', inline=False)
                      .set_footer(text=f'Vies : {self.lives}'))

        self.message = await self.ctx.send(embed=self.embed)
        await self.play()
