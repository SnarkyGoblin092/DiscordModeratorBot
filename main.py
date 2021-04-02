#!/usr/bin/python3
import discord
import os
import keep_alive
import asyncio
import typing
from discord.ext import commands
from discord.ext.commands import errors
from pretty_help import PrettyHelp
from urllib import request
import music_commands

description = 'A moderator bot for your server.'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', help_command=PrettyHelp(), description=description, intents=intents)


async def send_warning(message, title, description):
  formatted_description = (
    ':no_entry_sign:   **{0}**\n\n{1}'.format(title, description))
  warning = discord.Embed(title='Warning!', description=formatted_description, color = 0xff0000)

  await message.reply(embed=warning, delete_after=15)
  await asyncio.sleep(15)
  await message.delete()


async def send_command_usage(ctx):
  names = [ctx.command.name]
  names += ctx.command.aliases
  names = str(names).replace('\'', '').replace(', ', '|')
  signature = ctx.command.signature
  usage = f'```{bot.command_prefix}{names} {signature}```'
  
  embed = discord.Embed(title=ctx.command.name)
  embed.add_field(name='Usage', value=usage, inline=True)
  await ctx.send(embed=embed)


@bot.event
async def on_ready():
  print('Logged in as', bot.user)


@bot.event
async def on_command_error(ctx, exception):
  if isinstance(exception, errors.CommandNotFound):
    title = 'Unknown command!'
    description = 'The given command could not be found.'
    await send_warning(ctx.message, title, description)
  elif isinstance(exception, discord.ext.commands.BadArgument):
    await send_command_usage(ctx)
    

@bot.listen()
async def on_message(message):
  if not message.channel.name == 'music':
    if message.content.startswith(tuple(music_commands.commands)):
      music_bot = bot.get_user(235088799074484224)
      ch_music = bot.get_channel(821946547767345152)
      title = 'Wrong channel!'
      description = 'You can only use {0.mention}\'s command in {1.mention}.'.format(music_bot, ch_music)
      
      await send_warning(message, title, description)


@bot.listen()
async def on_command(ctx):
  ch_log = bot.get_channel(827374735830286347)
  user = ctx.author
  command = ctx.command
  channel = ctx.channel
  log_msg = '{0.mention} used `{1}` in {2.mention}'.format(user, command, channel)
  await ch_log.send(log_msg, allowed_mentions=discord.AllowedMentions.none())


@bot.check
async def pre_check(ctx):
  if ctx.channel.name == 'commands' or ctx.channel.name == 'bot-test':
    return True
  ch_commands = bot.get_channel(827374609234001970)
  ch_bot_test = bot.get_channel(827374679928471592)
  title = 'Wrong channel!'
  description = 'You can only use commands in {0.mention} and {1.mention}.'.format(ch_commands, ch_bot_test)
  
  await send_warning(ctx.message, title, description)


_ping_brief='For dumbasses'
_ping_desc='A command for your dumbass to have fun in your miserable life.'
@bot.command(name='ping', brief=_ping_brief, description=_ping_desc)
async def _ping(ctx):
  await ctx.message.reply('Pong!')


_nick_brief='Change nickname'
_nick_desc='Changes your name to whatever you write after it.'
@bot.command(name='nick', aliases=['nickname', 'name'], brief=_nick_brief, description=_nick_desc)
async def _nick(ctx, name : str):
  await ctx.author.edit(nick=name)


_insult_brief='Random insult'
_insult_desc='Insults you with a random insult.'
@bot.command(name='insult', aliases=['bother', 'curse'], brief=_insult_brief, description=_insult_desc)
async def _insult(ctx, target_user : discord.User = None):
  if not target_user:
    target_user = ctx.author

  random_insult = ''
  # Denote the long time the request takes by 'typing' to the channel
  async with ctx.typing():
    response = request.urlopen('https://evilinsult.com/generate_insult.php')
    random_insult = response.read().decode('UTF-8')

  await ctx.send("{0.mention} {1}".format(target_user, random_insult))


_pin_brief='Pin last message'
_pin_desc='Pins the last message of the channel that wasn\'t sent by the bot itself.'
@bot.command(name='pin', brief=_pin_brief, description=_pin_desc)
async def _pin(ctx):
  history=ctx.channel.history(limit=10)
  predicate = lambda message: not message.content.startswith(bot.command_prefix) and not message.author == bot.user
  last_user_made_message = await history.find(predicate)

  if last_user_made_message:
    await last_user_made_message.pin()
  else:
    await send_warning(ctx.message, 'Couldn\'t find any pinnable messages in the last 10 entries.')


_clear_brief='Erases messages'
_clear_desc='Deletes past messages based on given number.'
@bot.command(name='clear', aliases=['erase', 'clean'], brief=_clear_brief, description=_clear_desc)
async def _clear(ctx, channel : typing.Optional[discord.TextChannel], count : int = 1):
  await ctx.message.delete()

  if not channel:
    channel = ctx.channel

  history=channel.history(limit=count)
  async for message in history:
    await message.delete()


if __name__ == '__main__':
  # keeps the bot running
  keep_alive.keep_alive()

  # starts the bot
  bot.run(os.getenv('TOKEN'))
