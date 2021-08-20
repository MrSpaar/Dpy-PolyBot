from discord import HTTPException
from discord.ext import commands


class Erreurs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        handled = {
            commands.MissingPermissions: "❌ Tu n'as pas la permission de faire ça",
            commands.BotMissingPermissions: "❌ Je n'ai pas la permission de faire ça",
            commands.MissingRequiredArgument: f"❌ Il manque au moins un argument : `{getattr(getattr(error, 'param', ''), 'name', '')}`",
            commands.MemberNotFound: '❌ Membre inexistant',
            commands.PartialEmojiConversionFailure: "❌ Cette commande ne marche qu'avec les emojis custom",
            commands.CommandNotFound: '❌ Commande inexistante',
            commands.CheckFailure: '❌ Les commandes ne sont pas activées ici',
            commands.ChannelNotFound: '❌ Channel introuvable',
            commands.BadArgument: '❌ Les arguments doivent être des nombres entiers',
            commands.CommandOnCooldown: "❌ Commande en cooldown",
            commands.MaxConcurrencyReached: "❌ Il y a une limite d'une partie en même temps",
            commands.CommandInvokeError: {
                'channel': "❌ Tu n'es connecté à aucun channel",
                'string index': '❌ Erreur dans la conversion',
                'list index': "❌ Recherche invalide, aucun résultat trouvé",
                'UnknownObjectException': "❌ Recherche invalide, aucun résultat trouvé",
                'not enough values to unpack': "❌ Lancer invalide, exemples de lancers valides : `d6` `2d6` `2d6+3d9` `d6+20`",
                "KeyError: 'list'": "❌ Ville introuvable ou inexistante",
                'This video may be': "❌ Restriction d'âge, impossible de jouer la vidéo",
                'No video formats found': "❌ Aucun format vidéo trouvé, impossible de jouer la vidéo",
                'RecursionError': '❌ Trop de récursions, nombre trop grand',
                '4000': "❌ Mon message est trop long, impossible de l'envoyer",
            },
        }

        if type(error) not in handled:
            raise error

        error_entry = handled[type(error)]
        if isinstance(error_entry, dict):
            for key, value in error_entry.items():
                if key in str(error):
                    error_entry = value

        if ctx.command and ctx.command.brief:
            error_entry += f"\n❔ Exemple d'utilisation : `{self.bot.command_prefix}{ctx.command.name} {ctx.command.brief}`"

        await ctx.send(error_entry)


def setup(bot):
    bot.add_cog(Erreurs(bot))
