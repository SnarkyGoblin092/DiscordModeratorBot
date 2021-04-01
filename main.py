import discord
import os
import keep_alive
import features
from commands import commands_data

# creates the bot
client = discord.Client()


# checks if message starts with a command and returns the required role, 
# the command and the commands usage
def check_commands(message):
  for role, command_list in commands_data.items():
    for command, usage in command_list.items():
      if message.startswith(command):
        return [role, command, usage]
  return ["", "", ""]


# sends a warning when a command was used in the wrong channel
async def send_wrong_channel_warning(channel, author, message, role):
  embed_message = ""
  if role.name == "DJ":
    embed_message = discord.Embed(title="Figyelmeztetés!", description=":no_entry_sign:   **Rossz csatorna!**\n\nA {0.mention} joghoz tartozó parancsokat csak a {1.mention}-ban használhatod!".format(role, channel), color = 0xff0000)
  else:
    embed_message = discord.Embed(title="Figyelmeztetés!", description=":no_entry_sign:   **Rossz csatorna!**\n\nParancsokat csak a {0.mention}-ban használhatsz!".format(channel), color = 0xff0000)
  embed_message.set_author(name=author.display_name, icon_url=author.avatar_url)
  await message.delete()
  await message.channel.send(embed=embed_message)


# sends a warning when a command is used without permission
async def send_permission_warning(channel, author, message, role, command):
  embed_message = discord.Embed(title="Figyelmeztetés!", description=":no_entry_sign:   **Nincs jogod ehhez a parancshoz:** {0}\nSzükséges jog: {1}".format("`{}`".format(command), role.mention), color = 0xff0000)
  embed_message.set_author(name = author.display_name, icon_url=author.avatar_url)
  await message.delete()
  await channel.send(embed=embed_message)


# sends a warning that includes the usage of the used command when the command syntax is incorrect
async def send_use_warning(channel, author, message, role, command):
  usage = commands_data[role.name][command]
  title = "Figyelmeztetés!"
  description = ":x:   **Helytelen használat!**\n\n{0}".format(usage)
  embed_msg = discord.Embed(title=title, description=description, color=0xff9f21)
  embed_msg.set_author(name=author.display_name, icon_url=author.avatar_url)
  await message.delete()
  await channel.send(embed=embed_msg)


# updates the avatar of the bot
@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  with open("moderator.gif", "rb") as img:
    b = img.read()
  await client.user.edit(avatar=b)


# runs when a message is sent on the server
@client.event
async def on_message(message):
  msg = message.content
  msg_author = message.author
  msg_channel = message.channel

  # checks if the sender is the bot
  if msg_author == client.user:
    return

  # stores the channels used in the code
  commands_channel = client.get_channel(821759044905074698)
  music_channel = client.get_channel(821946547767345152)
  bot_log_channel = client.get_channel(821967330661498931)

  # manages the commands users try to run
  role_name, command, usage = check_commands(msg)
  if command:
    role = discord.utils.get(message.guild.roles, name=role_name)
    if not role in msg_author.roles:
      await send_permission_warning(msg_channel, msg_author, message, role, command)
      return

    dj_commands = commands_data["DJ"].keys()
    if command in dj_commands and not msg_channel.name == "music":
      await send_wrong_channel_warning(music_channel, msg_author, message, role)
    elif msg_channel.name == "commands" or msg_channel.name == "bot-test":
      if not msg.split(command, 1)[1]:
        await send_use_warning(msg_channel, msg_author, message, role, command)
        return
      log_msg = "{0.mention} used `{1}`".format(msg_author, msg)
      await bot_log_channel.send(log_msg)
      await features.call_function(msg_channel, msg_author, msg, command, role)
    else:
      await send_wrong_channel_warning(commands_channel, msg_author, message, role)


if __name__ == "__main__":
  # keeps the bot running
  keep_alive.keep_alive()

  # starts the bot
  client.run(os.getenv("TOKEN"))