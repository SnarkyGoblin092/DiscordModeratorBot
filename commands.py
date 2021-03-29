import discord

# stores the roles required to run commands
#command_groups = { "DJ", "Level1", "Level2" }

# stores the commands
commands_data = {
  "DJ" : {
    "!join" : "Unknown usage!",
    "!summon" : "Unknown usage!",
    "!fuckon" : "Unknown usage!",
    "!play" : "Unknown usage!",
    "!p" : "Unknown usage!",
    "!playtop" : "Unknown usage!",
    "!pt" : "Unknown usage!",
    "!ptop" : "Unknown usage!",
    "!playskip" : "Unknown usage!",
    "!ps" : "Unknown usage!",
    "!playnow" : "Unknown usage!",
    "!pn" : "Unknown usage!",
    "!search" : "Unknown usage!",
    "!find" : "Unknown usage!",
    "!soundcloud" : "Unknown usage!",
    "!sc" : "Unknown usage!",
    "!nowplaying" : "Unknown usage!",
    "!np" : "Unknown usage!",
    "!grab" : "Unknown usage!",
    "!save" : "Unknown usage!",
    "!yoink" : "Unknown usage!",
    "!seek" : "Unknown usage!",
    "!rewind" : "Unknown usage!",
    "!rwd" : "Unknown usage!",
    "!forward" : "Unknown usage!",
    "!fwd" : "Unknown usage!",
    "!replay" : "Unknown usage!",
    "!loop" : "Unknown usage!",
    "!repeat" : "Unknown usage!",
    "!skip" : "Unknown usage!",
    "!voteskip" : "Unknown usage!",
    "!next" : "Unknown usage!",
    "!s" : "Unknown usage!",
    "!forceskip" : "Unknown usage!",
    "!fs" : "Unknown usage!",
    "!fskip" : "Unknown usage!",
    "!pause" : "Unknown usage!",
    "!stop" : "Unknown usage!",
    "!resume" : "Unknown usage!",
    "!re" : "Unknown usage!",
    "!res" : "Unknown usage!",
    "!continue" : "Unknown usage!",
    "!lyrics" : "Unknown usage!",
    "!l" : "Unknown usage!",
    "!ly" : "Unknown usage!",
    "!disconnect" : "Unknown usage!",
    "!dc" : "Unknown usage!",
    "!leave" : "Unknown usage!",
    "!dis" : "Unknown usage!",
    "!fuckoff" : "Unknown usage!",
    "!queue" : "Unknown usage!",
    "!q" : "Unknown usage!",
    "!loopqueue" : "Unknown usage!",
    "!qloop" : "Unknown usage!",
    "!lq" : "Unknown usage!",
    "!queueloop" : "Unknown usage!",
    "!move" : "Unknown usage!",
    "!m" : "Unknown usage!",
    "!mv" : "Unknown usage!",
    "!skipto" : "Unknown usage!",
    "!st" : "Unknown usage!",
    "!shuffle" : "Unknown usage!",
    "!random" : "Unknown usage!",
    "!remove" : "Unknown usage!",
    "!rm" : "Unknown usage!",
    "!clear" : "Unknown usage!",
    "!cl" : "Unknown usage!",
    "!leavecleanup" : "Unknown usage!",
    "!lc" : "Unknown usage!",
    "!removedupes" : "Unknown usage!",
    "!rmd" : "Unknown usage!",
    "!rd" : "Unknown usage!",
    "!drm" : "Unknown usage!",
    "!sotd" : "Unknown usage!",
    "!playsotd" : "Unknown usage!",
    "!psotd" : "Unknown usage!",
    "!sotw" : "Unknown usage!",
    "!playsotw" : "Unknown usage!",
    "!psotw" : "Unknown usage!",
    "!sotm" : "Unknown usage!",
    "!playsotm" : "Unknown usage!",
    "!psotm" : "Unknown usage!",
    "!settings" : "Unknown usage!",
    "!setting" : "Unknown usage!",
    "!effects" : "Unknown usage!",
    "!effect" : "Unknown usage!",
    "!speed" : "Unknown usage!",
    "!bass" : "Unknown usage!",
    "!nightcore" : "Unknown usage!",
    "!slowed" : "Unknown usage!",
    "!volume" : "Unknown usage!",
    "!vol" : "Unknown usage!",
    "!prune" : "Unknown usage!",
    "!purge" : "Unknown usage!",
    "!clean" : "Unknown usage!",
    "!invite" : "Unknown usage!",
    "!links" : "Unknown usage!",
    "!info" : "Unknown usage!",
    "!shard" : "Unknown usage!",
    "!debug" : "Unknown usage!",
    "!ping" : "Unknown usage!",
    "!aliases" : "Unknown usage!"
  },
  "Level1" : {
    ".nick" : "Syntax: `.nick <becenév>`"
  },
  "Level2" : {
    ".print" : "Syntax: `.print <üzenet>`",
    ".say" : "Syntax : `.say <üzenet>`"
  }
}

# changes the nickname of the sender
async def change_nickname(channel, message, author):
  try:
    nickname = message.split(".nick", 1)[1]
    await author.edit(nick=nickname)
  except:
    embed_message = discord.Embed(title="Error!", description=":warning:   **Adminisztrátorok nevét nem tudom megváltoztatni!**", color = 0xff0000)
    await channel.send(embed=embed_message)

# sends a message to the bot to say in chat
async def bot_say(channel, message, command):
  await channel.send(message.split(command, 1)[1])