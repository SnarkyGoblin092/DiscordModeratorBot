import commands

async def call_function(channel, author, message, command, level):
  if command == ".nick":
    await commands.change_nickname(channel, message, author)
  elif command == ".print" or command == ".say":
    await commands.bot_say(channel, message, command)