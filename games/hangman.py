from discord import Embed, Color

from random import choice


class Hangman:
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.message = None
        self.embed = None

        self.word = choice([ligne.strip() for ligne in open('wordlist.txt')])
        self.guess = ['-']*len(self.word)
        self.lives, self.errors = 5, []

    async def start(self):
        self.embed = (Embed(title='Partie de pendu', color=Color.random())
                      .add_field(name='Mot', value=f"```{''.join(self.guess)}```", inline=False)
                      .add_field(name='Erreurs', value='```\u200b```', inline=False)
                      .set_footer(text=f'Vies : {self.lives}'))

        self.message = await self.ctx.send(embed=self.embed)
        await self.play()

    async def get_letter(self):
        letter = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author and len(m.content) == 1)
        await letter.delete()
        return letter.content.lower()

    async def play(self):
        letter = await self.get_letter()

        if letter in self.errors or letter in self.guess:
            await self.ctx.send('Tu as déjà envoyé cette lettre')
            return await self.play()
        elif letter not in self.word:
            self.lives -= 1
            self.errors.append(letter)
            self.embed.set_field_at(1, name='Erreurs', value=f"```{', '.join(self.errors)}```", inline=False)
            self.embed.set_footer(text=f'Vies : {self.lives}')
        else:
            self.guess = [letter if letter == char else self.guess[i] for i, char in enumerate(self.word)]
            self.embed.set_field_at(0, name='Mot', value=f"```{''.join(self.guess)}```", inline=False)

        await self.message.edit(embed=self.embed)

        if self.word == ''.join(self.guess):
            return await self.ctx.send('Bravo, tu as gagné ! :)')
        elif not self.lives:
            return await self.ctx.send(f'Perdu ! Le mot était `{self.word}`')
        else:
            await self.play()
