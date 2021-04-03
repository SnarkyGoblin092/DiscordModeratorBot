#!/usr/bin/python3
import discord
import os
import keep_alive
import typing
import asyncio
from discord.ext import commands
from discord.ext.commands import errors
from pretty_help import PrettyHelp
from urllib import request
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


async def send_warning(message, warning_type, title, description):
  formatted_description = ':no_entry_sign:   **{0}**\n\n{1}'.format(title, description)
  warning = discord.Embed(title=warning_type, description=formatted_description, color = 0xff0000)

  await message.reply(embed=warning, delete_after=5)
  await asyncio.sleep(5)
  await message.delete()


async def send_command_usage(ctx):
  names = [ctx.command.name]
  names += ctx.command.aliases
  names = str(names).replace('\'', '').replace(', ', '|')
  signature = ctx.command.signature
  usage = f'```{bot.command_prefix}{names} {signature}```'
  
  embed = discord.Embed(title=ctx.command.name)
  embed.add_field(name='Usage', value=usage, inline=True)
  await ctx.message.delete()
  await ctx.send(embed=embed, delete_after=15)


def extract_args(ctx):
  args = ''
  for arg in ctx.args:
    if not arg is ctx.args[0]:
      if not arg:
        continue
        
      if isinstance(arg, discord.TextChannel):
        args += f'#{arg} '
      elif isinstance(arg, discord.User):
        args += f'@{arg} '
      elif isinstance(arg, str):
        args += f'\'{arg}\' '
      else:
        args += f'{arg} '
  return args


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

  print('Logged in as', bot.user)
  await ch_log.send(f'{bot.user.mention} is online! :vulcan:')


@bot.event
async def on_command_error(ctx, exception):
  if isinstance(exception, errors.CommandNotFound):
    title = 'Unknown command!'
    description = 'The given command could not be found.'
    await send_warning(ctx.message, 'Notice!', title, description)
  elif isinstance(exception, discord.ext.commands.BadArgument):
    await send_command_usage(ctx)
  else:
    print(exception)


@bot.listen()
async def on_message(message):
  if not message.author.bot:
    music_command = message.content.startswith(tuple(music_commands.commands))
    if not message.channel is ch_music:
      if music_command:
        title = 'Wrong channel!'
        description = 'You can only use {0.mention}\'s command in {1.mention}.'.format(music_bot, ch_music)

        await send_warning(message, 'Warning!', title, description)
    else:
      if not music_command:
        title = 'Prohibited!'
        description = f'You can only send {music_bot.mention}\'s commands in this channel.'
        await send_warning(message, 'Warning!', title, description)  


@bot.listen()
async def on_command_completion(ctx):
  user = ctx.author
  command = ctx.command
  channel = ctx.channel
  args = extract_args(ctx).strip()
  log_msg = f'{user.mention} used in {channel.mention}```${command} {args}```'.strip()
  embed = discord.Embed(description=log_msg)

  await ch_log.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())


@bot.check
async def pre_check(ctx):
  if not ctx.channel is ch_music:
    return True


@bot.command(name='ping')
async def _ping(ctx):
  'Replies with "Pong!".'
  await ctx.message.reply('Pong!')


@bot.command(name='nick', aliases=['nickname', 'name'])
async def _nick(ctx, name : str = None):
  'Changes your name to whatever you want. You cannot have spaces in your name!'
  if not name == None: 
    await ctx.author.edit(nick=name)
  else:
    await send_command_usage(ctx)
    

@bot.command(name='insult', aliases=['bother', 'curse'])
async def _insult(ctx, target_user : discord.User = None):
  'Insults you or somebody else with a random insult.'

  if not target_user:
    target_user = ctx.author

  random_insult = ''
  # Denote the long time the request takes by 'typing' to the channel
  async with ctx.typing():
    response = request.urlopen('https://evilinsult.com/generate_insult.php')
    random_insult = response.read().decode('UTF-8')

  await ctx.send("{0.mention} {1}".format(target_user, random_insult))


@bot.command(name='pin')
async def _pin(ctx):
  'Pins the last message of the channel that wasn\'t sent by the bot itself.'
  history=ctx.channel.history(limit=10)
  predicate = lambda message: not message.content.startswith(bot.command_prefix) and not message.author == bot.user
  last_user_made_message = await history.find(predicate)

  if last_user_made_message:
    await last_user_made_message.pin()
  else:
    await send_warning(ctx.message, 'Notice!', '', 'Couldn\'t find any pinnable messages in the last 10 entries.')


@bot.command(name='clear', aliases=['erase', 'clean'])
async def _clear(ctx, channel : typing.Optional[discord.TextChannel], count : int = 1):
  'Deletes past messages based on given number.'
  
  await ctx.message.delete()
  if not channel:
    channel = ctx.channel
    
  history=channel.history(limit=count, oldest_first=False)
  async for message in history:
      await message.delete()


if __name__ == '__main__':
  # keeps the bot running
  keep_alive.keep_alive()
  # starts the bot
  bot.run(os.getenv('TOKEN'))