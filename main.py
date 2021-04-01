#!/usr/bin/python3
import discord
import os
import keep_alive
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
  
  await message.channel.send(embed=warning)


@bot.event
async def on_ready():
  print('Logged in as', bot.user)


@bot.event
async def on_command_error(ctx, exception):
  if type(exception) == errors.CommandNotFound:
    title = 'Unknown command!'
    description = 'The given command could not be found.'
    await send_warning(ctx.message, title, description)


@bot.listen()
async def on_message(message):
  if not message.channel.name == 'music':
    if message.content.startswith(tuple(music_commands.commands)):
      music_bot = bot.get_user(235088799074484224)
      ch_music = bot.get_channel(821946547767345152)
      title = 'Wrong channel!'
      description = 'You can only use {0.mention}\'s command in {1.mention}.'.format(music_bot, ch_music)
      
      await send_warning(message, title, description)


@bot.check
async def pre_check(ctx):
  if ctx.channel.name == 'commands' or ctx.channel.name == 'bot-test':
    return True
  ch_commands = bot.get_channel(821759044905074698)
  ch_bot_test = bot.get_channel(821714897582161940)
  title = 'Wrong channel!'
  description = 'You can only use commands in {0.mention} and {1.mention}.'.format(ch_commands, ch_bot_test)
  
  await send_warning(ctx.message, title, description)


_ping_brief='For dumbasses'
_ping_desc='A command for you dumbass to have fun in your miserable life.'
@bot.command(name='ping', brief=_ping_brief, description=_ping_desc)
async def _ping(ctx):
  await ctx.send('Pong!')


_nick_brief='Change nickname'
_nick_desc='A command that changes your name to whatever you write after it.'
@bot.command(name='nick', aliases=['nickname', 'name'], brief=_nick_brief, description=_nick_desc)
async def _nick(ctx, name : str):
  await ctx.author.edit(nick=name)


_insult_brief='Random insult'
_insult_desc='A command that insults you with a random insult.'
@bot.command(name='insult', aliases=['bother', 'insult_me', 'curse'], brief=_insult_brief, description=_insult_desc)
async def _insult(ctx):
  random_insult = ''
  # Denote the long time the request takes by 'typing' to the channel
  async with ctx.typing():
    response = request.urlopen('https://evilinsult.com/generate_insult.php')
    random_insult = response.read().decode('UTF-8')
  
  await ctx.send(random_insult)


_pin_brief='Pin last message'
_pin_desc='Pins the last message of the channel that wasn\'t commented by the bot itself.'
@bot.command(name='pin', brief=_pin_brief, description=_pin_desc)
async def _pin(ctx):
  history=ctx.channel.history(limit=10)
  predicate = lambda message: not message == ctx.message and not message.author == bot.user
  last_user_made_message = await history.find(predicate)

  if last_user_made_message:
    await last_user_made_message.pin()
  else:
    await send_warning(ctx.message, 'Couldn\'t find any pinnable messages in last 10 entries.')


if __name__ == '__main__':
  # keeps the bot running
  keep_alive.keep_alive()

  # starts the bot
  bot.run(os.getenv('TOKEN'))