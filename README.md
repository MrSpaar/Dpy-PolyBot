# Commands

---

PolyBot is a french, **multi-function bot for Discord**. For now, the bot's **private but open-source** !<br>
⚠️ Every link in this README leads to the corresponding source code or folder.<br>


### • 🧍 [User commands](https://github.com/MrSpaar/PolyBot/tree/master/commands)

|                                     Category                                |                      Commands                   |
|-----------------------------------------------------------------------------|-------------------------------------------------|
|[Fun](https://github.com/MrSpaar/PolyBot/blob/master/commands/fun.py)        | `chess` `hangman` `minesweeper` `toss` `roll`   |
|[Music](https://github.com/MrSpaar/PolyBot/blob/master/commands/music.py)    | `play` `pause` `skip` `remove` `leave`          |
|[Research](https://github.com/MrSpaar/PolyBot/blob/master/commands/search.py)| `twitch` `youtube` `wikipedia` `anime` `weather`|
|[Utility](https://github.com/MrSpaar/PolyBot/blob/master/commands/utility.py)| `help` `poll` `source` `pfp` `emoji` `translate`|
|[Maths](https://github.com/MrSpaar/PolyBot/blob/master/commands/maths.py)    | `base` `binary` `hexadecimal` `compute`         |
|[Levels](https://github.com/MrSpaar/PolyBot/blob/master/commands/levels.py)  | `rank` `levels`                                 |

### • 🔒 [Admin commands](https://github.com/MrSpaar/PolyBot/tree/master/admin)

|                                        Category                                |                                  Commands                               |
|--------------------------------------------------------------------------------|-------------------------------------------------------------------------|
|[Moderation](https://github.com/MrSpaar/PolyBot/blob/master/admin/moderation.py)| `mute` `automute` `unmute` `clear` `kick` `ban` `unban` `clone` `cancel`|
|[Infos](https://github.com/MrSpaar/PolyBot/blob/master/admin/informations.py)   | `serverinfo` `userinfo` `roleinfo` `channelinfo` `lastjoins`            |
|[Setup](https://github.com/MrSpaar/PolyBot/blob/master/admin/setup.py)          | `set` `settings`                                                        |

⚠️ For mute related commands, you'll need to set a mute role: `!set mute <@role>`

This bot uses [MongoDB](https://www.mongodb.com/cloud/atlas). If you plan copy pasting the whole code, you'll need to create a database named `data`, containing 3 collections: `pending`, `users` and `settings`.

# Extra modules

---

### • 📈 [Leveling system](https://github.com/MrSpaar/PolyBot/blob/master/events/levels.py)

The system have the **same xp curve as [Mee6](https://mee6.xyz/)**. <br>
Use `!set channel <#channel>` to set the bot's channel, where it will announce rank ups.<br>
`!rank` will show your current xp, level and leaderboard position.<br>
`!levels` will show a leaderboard, each page contains 10 users along with their xp and level.

### • 💬 [OpenAI Chatbot](https://github.com/MrSpaar/PolyBot/blob/master/events/openai.py)

This module is a WIP but allows to "talk" with PolyBot:
![Example](https://i.imgur.com/V1Eikkc.png)
To get an API key, you need to join [OpenAI's waitlist](https://share.hsforms.com/1Lfc7WtPLRk2ppXhPjcYY-A4sk30). <br>
⚠️ Answers might not be accurate or can be repetitive.

### • ⏲️ [Temporary channels](https://github.com/MrSpaar/PolyBot/blob/master/events/channels.py)

This module generates temporary voice channels :

- Every voice channel that contain [this prefix](https://github.com/MrSpaar/PolyBot/blob/master/events/channels.py#L18) will generate a temporary channel when a member joins it.
- A text channel is generated along with the voice channel.
- Both of them are deleted when the voice channel is empty.

### • 📝 [Logs](https://github.com/MrSpaar/PolyBot/blob/master/events/logs.py)

Log channel can be set using `!set logs <#channel>`.

|            Log             |                  Informations showed                  |
|----------------------------|-------------------------------------------------------|
|Message deletion            | Author, message content and attachments               |
|Member joins                | Member mention                                        |
|Member leaves               | Member display name and tag, reason (ban, kick, ...)  |
|Member unban                | Member unbanned, by who and reason                    |
|Nick modification           | Previous and new nicknames and by who                 |
|Role modifications          | Role added or removed, from who and by who            |
|Discord profile modification| Previous and new nick or tag                          |
|Server invite creation      | Invite link, author, expire date, max uses and channel|

### • ❌ [Errors handling](https://github.com/MrSpaar/PolyBot/blob/master/events/errors.py)

This module is a general error handler and isn't command specific.<br>
When an error occurs, it will send a message describing the error and giving an example.<br>

Here is a list of current handled errors:
- User missing permission
- Bot missing permission
- Missing required command argument
- Member not found
- Emoji conversion failure (Commands only supporting custom emojis arguments)
- Command not found
- Using a command in a forbidden channel
- Channel not found (either voc or text)
- Argument conversion error (str instead of int for instance)
- Command on cooldown
- Maximum concurrency reached (game commands can only be run one at a time in the same channel)
- Member using music commands but not connected to any channel
- Base conversion error
- No results for research commands
- Invalid dice rolls
- City not found (weather command)
- Message is too long to send
- Age restricted videos
- Some videos can't be played by the bot
- Too much recursions (base conversion command)