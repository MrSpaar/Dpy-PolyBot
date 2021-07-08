from discord.ext import commands


class Erreurs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        invoke_errors = {
            'channel': "❌ Tu n'es connecté à aucun channel",
            'string index': '❌ Erreur dans la conversion',
            'list index': "❌ Recherche invalide, aucuns résultats trouvés",
            'UnknownObjectException': "❌ Recherche invalide, aucuns résultats trouvés",
            'not enough values to unpack': "❌ Lancer invalide, exemples de lancers valides : `d6` `2d6` `2d6+3d9` `d6+20`",
            'This field is required': "❌ Nom de catégorie invalide",
            "KeyError: 'list'": "❌ Ville introuvable ou inexistante",
            "2048": "❌ Mon message est trop long, impossible de l'envoyer",
            "This video may be": "❌ Restriction d'âge, impossible de jouer la vidéo",
            "No video formats found": "❌ Aucun format vidéo trouvé, impossible de jouer la vidéo",
            "RecursionError": '❌ Trop de récursions, nombre trop grand'
        }

        param = error.param.name if isinstance(error, commands.MissingRequiredArgument) else ''
        arg, = [value for key, value in invoke_errors.items() if key in str(error)] or ['']

        basic_errors = {
            commands.MissingPermissions: "❌ Tu n'as pas la permission de faire ça",
            commands.BotMissingPermissions: "❌ Je n'ai pas la permission de faire ça",
            commands.MissingRequiredArgument: f"❌ Il manque au moins un argument : `{param}`",
            commands.MemberNotFound: '❌ Membre inexistant',
            commands.PartialEmojiConversionFailure: "❌ Cette commande ne marche qu'avec les emojis custom",
            commands.CommandInvokeError: arg,
            commands.CommandNotFound: '❌ Commande inexistante',
            commands.CheckFailure: '❌ Tu ne peux pas faire ça',
            commands.ChannelNotFound: '❌ Channel introuvable',
            commands.BadArgument: '❌ Les arguments doivent être des nombres entiers',
            commands.CommandOnCooldown: "❌ Commande en cooldown",
            commands.MaxConcurrencyReached: "❌ Il y a une limite d'une partie en même temps",
        }

        for error_type, msg in basic_errors.items():
            if isinstance(error, error_type) and msg:
                if ctx.command and ctx.command.brief:
                    msg = f"{msg}\n❔ Exemple d'utilisation : `{self.bot.command_prefix}{ctx.command.name} {ctx.command.brief}`"

                await ctx.send(msg)
                return

        if ctx.message and ctx.command:
            cmd = f'{self.bot.command_prefix}{ctx.invoked_with}'
            url = ctx.message.to_reference().jump_url
            print(f'[Erreur] "{cmd}{ctx.message.content.strip(cmd)}" ({url}):')
            print(error, end='\n\n')
        else:
            raise error


def setup(bot):
    bot.add_cog(Erreurs(bot))
