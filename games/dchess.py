from discord import File, Embed

from chess import Board, Move
from chess.svg import board
from cairosvg import svg2png
from os import remove


class Chess:
    def __init__(self, bot, ctx, opponent):
        self.bot = bot
        self.ctx = ctx
        self.cur = [ctx.author, opponent]
        self.opponent = opponent
        self.end = False
        self.message = None
        self.board = Board()

    async def check_board(self):
        if self.board.is_checkmate():
            await self.ctx.send(f'{self.cur[0].mention} a gagné la partie !')
            self.end = True
        elif self.board.is_game_over():
            await self.ctx.send('Égalité, personne ne gagne')
            self.end = True

    async def send_message(self, move=None, color=0x00000, text='', init=False):
        if self.message:
            await self.message.delete()

        b = board(self.board, lastmove=Move.from_uci(move)) if move else board(self.board)
        svg2png(bytestring=b, write_to='output.png')
        footer = '2 minutes par coups' + f' • Tour de {self.cur[1].display_name}' if not init else ''

        embed = (Embed(color=color, description=text)
                 .set_footer(text=footer)
                 .set_image(url="attachment://board.png")
                 .set_author(name=f'{self.opponent.name} contre {self.ctx.author.name}',
                             icon_url=self.opponent.avatar_url))

        self.message = await self.ctx.send(embed=embed, file=File('output.png', 'board.png'))
        remove('output.png')

    async def start(self):
        await self.send_message(init=True)
        await self.message.add_reaction('✅')
        await self.message.add_reaction('❌')

        try:
            react = await self.bot.wait_for('reaction_add', timeout=300,
                                            check=lambda r, u: (str(r) == '✅' or str(r) == '❌') and u == self.opponent)
        except:
            await self.send_message(color=0xe74c3c, text="❌ L'adversaire n'a pas accepté la partie à temps")
            return False

        if str(react[0]) == '❌':
            await self.send_message(color=0xe74c3c, text="❌ L'adversaire à refusé la partie")
            return False

        await self.send_message(color=0xfffff)
        return True

    async def turn(self):
        try:
            move = await self.bot.wait_for('message', timeout=120, check=lambda m: m.author == self.cur[0])

            if move.content in ['ff', 'resign', 'abandon', 'abandonner']:
                await self.ctx.send(f'{self.cur[0].mention} a abandonné la partie')

            valid = move.content in [str(move) for move in self.board.legal_moves]
            is_move = 4 <= len(move.content) <= 5 and sum(c.isdigit() for c in move.content) == 2

            if not valid and is_move:
                await move.delete(delay=3)
                await self.ctx.send('❌ Mouvement invalide', delete_after=3)
                return await self.turn()

            if not valid and not is_move:
                return await self.turn()

            self.board.push_san(move.content)
            await move.delete()
            await self.send_message(move.content, 0xfffff)
        except:
            await self.ctx.send(f'Temps de réflexion écoulé, {self.cur[1].mention} a gagné')
            return

    async def play(self):
        while not self.end:
            await self.turn()
            await self.check_board()
            self.cur[0], self.cur[1] = self.cur[1], self.cur[0]
