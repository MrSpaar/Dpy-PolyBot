# Commandes

---

PolyBot est **un bot discord multi-fonction**. Pour l'instant, il est **semi-privé mais open-source** !<br>
⚠️ Chaque lien mène vers le code source ou le dossier lui correspondant.<br>


### • 🧍 [Commandes utilisateur](https://github.com/MrSpaar/PolyBot/tree/master/commands)

|                                          Category                                         |                      Commands                   |
|-------------------------------------------------------------------------------------------|-------------------------------------------------|
|[Fun](https://github.com/MrSpaar/PolyBot/blob/master/commands/fun.py)                      | `chess` `hangman` `minesweeper` `toss` `roll`   |
|[Musique](https://github.com/MrSpaar/PolyBot/blob/master/commands/music.py)                | `play` `pause` `skip` `remove` `leave`          |
|[Recherche](https://github.com/MrSpaar/PolyBot/blob/master/commands/search.py)             | `twitch` `youtube` `wikipedia` `anime` `weather`|
|[Utilitaire](https://github.com/MrSpaar/PolyBot/blob/master/commands/utility.py)           | `help` `poll` `source` `pfp` `emoji` `translate`|
|[Maths](https://github.com/MrSpaar/PolyBot/blob/master/commands/maths.py)                  | `base` `binary` `hexadecimal` `compute`         |
|[Niveaux](https://github.com/MrSpaar/PolyBot/blob/master/commands/levels.py)               | `rank` `levels`                                 |
|[Channels Temporaires](https://github.com/MrSpaar/PolyBot/blob/master/commands/channels.py)| `voc rename` `voc private` `voc owner           |`

### • 🔒 [Commandes admin](https://github.com/MrSpaar/PolyBot/tree/master/admin)

|                                        Category                                |                                  Commands                               |
|--------------------------------------------------------------------------------|-------------------------------------------------------------------------|
|[Modération](https://github.com/MrSpaar/PolyBot/blob/master/admin/moderation.py)| `mute` `automute` `unmute` `clear` `kick` `ban` `unban` `clone` `cancel`|
|[Infos](https://github.com/MrSpaar/PolyBot/blob/master/admin/informations.py)   | `serverinfo` `userinfo` `roleinfo` `channelinfo` `lastjoins`            |
|[Setup](https://github.com/MrSpaar/PolyBot/blob/master/admin/setup.py)          | `set` `settings`                                                        |

⚠️ La création d'un rôle `muted` est automatique mais si vous en voulez un spécifique : `!set mute <@role>`

# Modules supplémentaires

---

### • 📈 [Système d'expérience](https://github.com/MrSpaar/PolyBot/blob/master/events/levels.py)

Le système a la **même courbe d'xp que [Mee6](https://mee6.xyz/)**. <br>
Ecrivez `!set channel <#channel>` pour définir le salon où le bot fait ses annonces de level up.<br>
`!rank` vous montrera votre niveau, expérience et position dans le classement du serveur.<br>
`!levels` vous montrera le classement du serveur par page de 10.

### • 💬 [Chatbot OpenAI](https://github.com/MrSpaar/PolyBot/blob/master/events/openai.py)

Ce module est en cours d'affinage mais vous permet de "parler" avec PolyBot :
![Example](https://i.imgur.com/V1Eikkc.png)
Pour obtenir une clé API, vous devrez rejoindre la [liste d'attente OpenAI](https://share.hsforms.com/1Lfc7WtPLRk2ppXhPjcYY-A4sk30). <br>
⚠️ Les réponses peuvent être répétitives ou imprécises. Je ne suis en aucun cas responsable des réponses données par le bot.

### • ⏲️ [Channels temporaires](https://github.com/MrSpaar/PolyBot/blob/master/events/channels.py)

Ce module permet d'avoir des channels vocaux temporaires :

- Chaque channel contenant [ce prefix](https://github.com/MrSpaar/PolyBot/blob/master/events/channels.py#L18) génèrera un channel tempaire dès que quelqu'un le rejoindra.
- Un channel écrit est généré et lié avec le channel temporaire.
- Les deux sont supprimés dès que le channel vocal est vide.

### • 📝 [Logs](https://github.com/MrSpaar/PolyBot/blob/master/events/logs.py)

Ecrivez `!set logs <#channel>` pour définir le channel contenant les logs.

|           Log            |                Informations affichées                  |
|--------------------------|--------------------------------------------------------|
|Messages supprimés        | Autheur, contenu et images (si il y en a)              |
|Nouveau membre            | Mention                                                |
|Départ d'un membre        | Pseudo, ID et raison (ban, kick, ...)                  |
|Membre unban              | Pseudo, par qui et raison                              |
|Changement de surnom      | Ancien et nouveau surnom et par qui                    |
|Ajout/Suppression de rôles| Rôle ajouté ou enlevé, de qui et par qui               |
|Modification de profile   | Ancien et nouveau pseudo et/ou tag                     |
|Création d'invitation     | Lien, autheur, date d'expiration, nombre d'utilisations|

### • ❌ [Gestion d'erreurs](https://github.com/MrSpaar/PolyBot/blob/master/events/errors.py)

Ce module permet d'afficher des messages d'erreurs.<br>
A chaque erreur, un message suivi d'un exemple est envoyé.<br>

Liste des erreurs actuellement gérées :
- Permission manquante
- Argument manquant
- Membre inconnu / pas trouvé
- Emoji non custom
- Commande inconnue / pas trouvée
- Channel inconnu / pas trouvé
- Erreur de conversion d'arguments
- Cooldown non terminé
- Commande déjà en cours d'utilisation
- Trop grand nombre de récursions
- Utilisation du module musique sans être connecté à un channel
- Vidéo soumise à une limite d'age
- Aucun résultat trouvé (pour les commandes de recherche)
- Ville inconnue / pas trouvée (commande météo)