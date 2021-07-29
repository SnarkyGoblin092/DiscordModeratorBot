#!/usr/bin/python3
import discord
import os
import typing
import aiohttp
import tempfile
import datetime
import textwrap
from pathlib import Path
from discord.errors import DiscordServerError
from discord.ext import commands, tasks
from pretty_help import PrettyHelp
import music_commands
import forum_scraper


description = 'A moderator bot for your server.'
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', help_command=PrettyHelp(), description=description, intents=intents)
run_indicator = Path(f'{tempfile.gettempdir()}/dc_moderator_bot')


class WrongChannelError(commands.CommandError):
    'Raised when the user wants to run a command in the channel of music bot.'
    pass


class InsultAPIError(Exception):
    'Raised when the Evil Insult API having issues.'
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
    async with aiohttp.ClientSession() as client:
        async with client.get('https://evilinsult.com/generate_insult.php') as response:
            if not response.status == 200:
                raise InsultAPIError

            return await response.text()


@tasks.loop(minutes=1)
async def task_dealwatch():
    try:
        with open('forum_scraper_last_message_id.txt', 'r') as f:
            last_message_id = int(f.readline())
    except (FileNotFoundError, ValueError):
        with open('forum_scraper_last_message_id.txt', 'w') as f:
            last_message_id = 90000 # A high default value
            f.write(str(last_message_id))

    try:
        forum_messages = await forum_scraper.scrape_recursively(from_message_id=last_message_id+1)
    except forum_scraper.NetworkErrorDuringScraping:
        print('Network error occured during web scraping. task_dealwatch is skipping one iteration now...')
        return


    if forum_messages:
        # Using TextWrapper to limit the message size (DC allows the maximum of 2000 chars)
        text_wrapper = textwrap.TextWrapper(width=1900, break_long_words=True)
        for message in forum_messages:
            cutted_text = text_wrapper.wrap(message.text)
            # Send long messages in "chunks"
            for chunk in cutted_text:
                embed = discord.Embed(title=message.author_nick)
                embed.add_field(name=message.datetime, value=chunk)
                await ch_dealwatch.send(embed=embed)

        last_message_id = forum_messages[-1].id
        with open('forum_scraper_last_message_id.txt', 'w') as f:
            f.write(str(last_message_id))


@bot.event
async def on_ready():
    global music_bot
    global ch_music
    global ch_log
    global ch_commands
    global ch_bot_test
    global ch_dealwatch
    global insult_api_session

    insult_api_session = aiohttp.ClientSession()

    music_bot = bot.get_user(235088799074484224)
    ch_music = bot.get_channel(821946547767345152)
    ch_log = bot.get_channel(827374735830286347)
    ch_commands = bot.get_channel(827374609234001970)
    ch_bot_test = bot.get_channel(827374679928471592)
    ch_dealwatch = bot.get_channel(832438420672086066)

    task_dealwatch.start()

    print('Logged in as', bot.user, flush=True)
    if run_indicator.exists():
        await ch_log.send('I crashed into a tree... :worried: But I\'m back!')    
    else:
        await ch_log.send('I\'m fresh and back in business! :vulcan:')
        run_indicator.touch()


@bot.listen()
async def on_message(message):
    author = message.author
    command_str = message.content.partition(' ')[0]
    if not command_str.startswith(music_commands.command_prefix) or author.bot:
        return

    is_music_command = command_str in music_commands.commands
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

    moderator = discord.utils.get(ctx.guild.roles, id=821838588017639516)

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

    elif isinstance(exception, commands.MissingRole):
        title = 'Warning!'
        sub_title ='You are not allowed to use this command!'
        description = f'You are required to have {moderator.mention} role to use this command.'
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
    'Changes your name to whatever you want. No spaces allowed! Don\'t give any parameters to reset your name.'
    await ctx.author.edit(nick=name)

    if name:
        msg = 'Nickname set!'
    else:
        msg = 'Nickname cleared!'
    await ctx.reply(msg)


@bot.command(name='insult', aliases=['bother', 'curse'])
async def _insult(ctx, target_user : discord.User = None):
    'Insults you or somebody else with a random insult.'

    if not target_user:
        target_user = ctx.author

    try:
        # Denote the time consuming request by 'typing' to the channel
        async with ctx.typing():
            random_insult = await get_random_insult()
        msg = f'{target_user.mention} {random_insult}'
        await ctx.reply(msg)

    except InsultAPIError:
        title='Error!'
        sub_title='Insult API error!'
        description='Seems like the insult API having issues right now! Try again later.'
        await send_warning(reply_to=ctx.message, title=title, sub_title=sub_title, description=description, delete_after=10)
        await ctx.message.delete(delay=10)


@bot.command(name='pin', aliases=['save'])
@commands.has_role('Admin')
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
@commands.has_role("Admin")
async def _clear(ctx, channel : typing.Optional[discord.TextChannel], count : int = 1):
    'Deletes past messages based on given number. Cannot delete past 2 weeks.'
    if not channel:
        channel = ctx.channel

    async with ctx.typing():
        if channel is ctx.channel:
            await ctx.message.delete()

        # Don't delete past two weeks
        two_weeks_ago = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
        deleted_messages = await channel.purge(limit=count, after=two_weeks_ago)
    
    msg = f'Deleted {len(deleted_messages)} entries!'
    await ctx.send(msg, delete_after=10)


async def quit():
    await ch_log.send('Imma\' head out! :v:')
    run_indicator.unlink(missing_ok=True)


if __name__ == '__main__':
    # starts the bot
    loop = bot.loop

    try:
        loop.run_until_complete(bot.start(os.getenv('TOKEN')))
    except KeyboardInterrupt:
        loop.run_until_complete(quit())
    finally:
        loop.close()