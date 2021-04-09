#!/usr/bin/python3
import discord
import os
import typing
import aiohttp
from discord.ext import commands
from pretty_help import PrettyHelp
import music_commands

description = 'A moderator bot for your server.'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', help_command=PrettyHelp(), description=description, intents=intents)

# bots
music_bot = None
# channels
ch_music = None
ch_log = None
ch_commands = None
ch_bot_test = None


class WrongChannelError(commands.CommandError):
  'Raised when the user wants to run a command in the channel of music bot.'
  pass


async def send_warning(reply_to, title, sub_title, description, delete_after=None):
  'Sends a custom warning by replying to a message.'
  formatted_description = (
    f':no_entry_sign:\t**{sub_title}**\n\n{description}'
  )
  warning = discord.Embed(title=title, description=formatted_description, color=0xff0000)
  return await reply_to.reply(embed=warning, delete_after=delete_after)


async def send_command_usage(reply_to, command, delete_after=None):
  'Sends a command\'s usage by replying to a message.'
  names = '|'.join([command.name] + command.aliases)
  signature = command.signature
  usage = f'```{bot.command_prefix}[{names}] {signature}```'

  embed = discord.Embed(title=command.name)
  embed.add_field(name='Usage', value=usage, inline=True)
  return await reply_to.reply(embed=embed, delete_after=delete_after)


async def get_random_insult():
  'Gets a random insult asynchronously using the EvilInsult API'
  async with aiohttp.ClientSession() as session:
    async with session.get('https://evilinsult.com/generate_insult.php') as response:
      return await response.text()


@bot.event
async def on_ready():
  global music_bot
  global ch_music
  global ch_log
  global ch_commands
  global ch_bot_test

  music_bot = bot.get_user(235088799074484224)
  ch_music = bot.get_channel(821946547767345152)
  ch_log = bot.get_channel(827374735830286347)
  ch_commands = bot.get_channel(827374609234001970)
  ch_bot_test = bot.get_channel(827374679928471592)

  print('Logged in as', bot.user, flush=True)
  await ch_log.send(f'{bot.user.mention} is online! :vulcan:')


@bot.listen()
async def on_message(message):
  if not message.content.startswith(music_commands.command_prefix) or message.author.bot:
    return

  is_music_command = message.content.startswith(music_commands.commands)
  if is_music_command and not message.channel is ch_music:
    title = 'Warning!'
    sub_title = 'Wrong channel!'
    description = f'You can only use {music_bot.mention}\'s command in {ch_music.mention}.'
    await send_warning(reply_to=message, title=title, sub_title=sub_title, description=description, delete_after=10)
    await message.delete(delay=10)


@bot.check
async def check_channel(ctx):
  if ctx.channel is ch_music:
    raise WrongChannelError

  return True


@bot.event
async def on_command_error(ctx, exception):
  if isinstance(exception, commands.CommandNotFound):
    title = 'Unknown command!'
    description = 'The given command could not be found.'
    await send_warning(reply_to=ctx.message, title='Notice!', sub_title=title, description=description, delete_after=10)

  elif isinstance(exception, commands.BadArgument):
    title = 'Error!'
    sub_title = 'Bad argument!'
    description = 'Command got a bad argument.'
    await send_warning(reply_to=ctx.message, title=title, sub_title=sub_title, description=description, delete_after=10)
    await send_command_usage(reply_to=ctx.message, command=ctx.command, delete_after=10)

  elif isinstance(exception, WrongChannelError):
    title = 'Warning!'
    sub_title = 'Prohibited!'
    description = f'You can only use {music_bot.mention}\'s commands in this channel.'
    await send_warning(reply_to=ctx.message, title=title, sub_title=sub_title, description=description, delete_after=10)

  else:
    title = 'Error!'
    sub_title = 'Unknown error!'
    description = f'An unknown command error occured!\nException: {exception}'
    await send_warning(reply_to=ctx.message, title=title, sub_title=sub_title, description=description, delete_after=10)
  
  await ctx.message.delete(delay=10)


@bot.listen()
async def on_command_completion(ctx):
  user = ctx.author
  channel = ctx.channel
  cmd_msg = ctx.message
  log_msg = f'{user.mention} used a command in {channel.mention} \n```{cmd_msg.clean_content}```'

  embed = discord.Embed(description=log_msg)
  await ch_log.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())


@bot.command(name='ping')
async def _ping(ctx):
  'Replies with "Pong!".'
  await ctx.message.reply('Pong!')


@bot.command(name='nick', aliases=['nickname', 'name'])
async def _nick(ctx, name : str = None):
  'Changes your name to whatever you want. You cannot have spaces in your name!'
  if name: 
    await ctx.author.edit(nick=name)
  else:
    await send_command_usage(reply_to=ctx.message, command=ctx.command, delete_after=10)
    await ctx.message.delete(delay=10)


@bot.command(name='insult', aliases=['bother', 'curse'])
async def _insult(ctx, target_user : discord.User = None):
  'Insults you or somebody else with a random insult.'

  if not target_user:
    target_user = ctx.author

  # Denote the time consuming request by 'typing' to the channel
  async with ctx.typing():
    random_insult = await get_random_insult()

  msg = f'{target_user.mention} {random_insult}'
  await ctx.message.reply(msg)


@bot.command(name='pin')
async def _pin(ctx):
  'Pins the last message of the channel that\'s not a command nor sent by the bot.'
  history=ctx.channel.history(limit=10)
  predicate = lambda msg: not msg.content.startswith(ctx.prefix) and not msg.author.bot
  last_user_made_message = await history.find(predicate)

  if last_user_made_message:
    await last_user_made_message.pin()
  else:
    title = 'Notice!'
    description = 'Couldn\'t find any pinnable messages in the last 10 entries.'
    await send_warning(reply_to=ctx.message, title=title, sub_title='', description=description, delete_after=10)
    await ctx.message.delete(delay=10)


@bot.command(name='clear', aliases=['erase', 'clean', 'purge'])
async def _clear(ctx, channel : typing.Optional[discord.TextChannel], count : int = 1):
  'Deletes past messages based on given number.'
  if not channel:
    channel = ctx.channel

  async with ctx.typing():
    if channel is ctx.channel:
      await ctx.message.delete()
    deleted_messages = await channel.purge(limit=count)
  
  msg = f'Deleted {len(deleted_messages)} entries!'
  await ctx.send(msg, delete_after=10)


if __name__ == '__main__':
  # starts the bot
  bot.run(os.getenv('TOKEN'))