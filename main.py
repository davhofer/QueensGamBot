import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import logging
import random
import datetime
from chessdotcom import get_player_stats, client
from gpiozero import CPUTemperature
import nest_asyncio
import time
import subprocess

from asvzBot import asvz_signup, get_driver, get_signup_time

# ------------------------------
# SETUP
# ------------------------------
nest_asyncio.apply()


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

with open('data.json') as f:
    data = json.load(f)
    f.close()

with open('quotes.json') as f:
    quotes = json.load(f)
    f.close()

insults = data['insults']
name_mapping = data['name_mapping']
running_since = datetime.datetime.now()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# CHECK/CHANGE logging
# Log commands used


# ------------------------------
# BOT
# ------------------------------
description = ''' Queens GamBot'''

intents = discord.Intents.default()
#intents.members = True

bot = commands.Bot(command_prefix='$',description=description,intents=intents)

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await message.guild.get_member(bot.user.id).edit(nick="Queens GamBot")


# ------------------------------
# COMMANDS
# ------------------------------
@bot.before_invoke
async def preprocess(ctx):
    #print("before invoke")
    f = open('commands.log','a')
    msg = ctx.message.content
    appendix = ''

    for u in ctx.message.mentions:
        msg = msg.replace('<@!' + str(u.id) + '>', '@' + u.nick + '(' + str(u) + ')')
    e = str(datetime.datetime.today()) + ' ' + str(datetime.datetime.now()) + '   ' + str(ctx.author) + ': "' + msg + '"' + '\n'
    f.write(e)
    f.close()
    return

#
# --------------- Various Commands ---------------
#
@bot.command()
async def roll(ctx):
    """Get a random number between 0 and 100"""
    result = str(random.randint(0,100))
    await ctx.send(result)

@bot.command()
async def choose(ctx, *choices: str):
    """Choose between multiple choices"""
    await ctx.send(random.choice(choices))

@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        if random.randint(1,100) > 90:
            await ctx.send('{0.subcommand_passed} is kinda cool'.format(ctx))
        else:
            await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

@cool.command(name='david',aliases=['@david','dave'])
async def _bot(ctx):
    """Is david cool?"""
    await ctx.send('Yes, {0} is cool.'.format(ctx.subcommand_passed))

@cool.command(name='lukas',aliases=['Lukas','Kazar','@KazarEzClap','kazar'])
async def _bot(ctx):
    """Is lukas cool?"""
    await ctx.send('Yes, {0} is cool.'.format(ctx.subcommand_passed))



# @bot.command()
# async def author(ctx):
#     """The dude who wrote this"""
#     await ctx.send("I created myself. Jokes on you.")
#


@bot.command()
async def ping(ctx):
    """Check if I'm still alive"""
    await ctx.send(":ping_pong: Pong!")


@bot.command()
async def joined(ctx, *, member: discord.Member):
    """see when a specific member joined"""
    await ctx.send('{0.name} joined on {0.joined_at}'.format(member))


@bot.command()
async def inspire(ctx):
    """inspires you! Sends a quote from inspirobot.me, an AI that creates "inspirational quotes" ;) \n Disclaimer: these quotes are not our own and are created artificially!"""
    msg = await ctx.send("Please be patient, image is loading...")

    if not os.system('cd inspirobot-bot && node lib/inspirobot.js 1') == 0:
            await ctx.send("download go ded, sorry :frowning:")
            return
    counter = 0
    while True:
        if counter==8:
            await ctx.send("Download error. Please try again.")
            return
        time.sleep(1)
        counter+=1
        for fname in os.listdir('./inspirobot-bot/'):
            if fname.endswith('.jpg'):
                await msg.delete()
                await ctx.send(file=discord.File('./inspirobot-bot/'+fname))
                #move file
                os.rename('./inspirobot-bot/'+fname,'./inspirobot-bot/img/'+fname)
                return





@bot.command()
async def say(ctx, *, msg: str):
    """say a message out loud"""
    show = await ctx.send(msg, tts=True)
    await show.delete()



#
# --------------- QUOTES ---------------
#
@bot.command()
async def q(ctx, name: str, *, quote: str):
    """Add a quote for someone. To see quotes, use $quote"""
    if not (len(ctx.message.mentions) == 0 or not name.startswith('<@')):
        name = ctx.message.mentions[0].name
    if name not in quotes.keys():
        quotes[name] = [quote]
    else:
        quotes[name].append(quote)
    with open('quotes.json', 'w') as f:
         json.dump(quotes, f)
         f.close()
    await ctx.send("Quote for {0} added!".format(name))


@bot.command()
async def quote(ctx, name: str, number=None):
    """Get quotes of someone. To add quotes, use $q. You can leave <number> out to get a random quote, or write 'all' to see all quotes."""
    if not len(ctx.message.mentions) == 0:
        name = ctx.message.mentions[0].name
        nick = ctx.message.mentions[0].nick
    else:
        nick = name
    if name not in quotes.keys():
        await ctx.send("{0} doesn't have any quotes yet!".format(nick))
        return
    if number==None:
        quote = random.choice(quotes[name])
        await ctx.send("'{0}' ~{1}".format(quote,nick))
    elif number=='all':
        #display all quotes
        msg = ""
        for i in range(len(quotes[name])):
            msg += str(i+1) + ". " + quotes[name][i] +"\n"
        await ctx.send(msg)
    else:
        try:
            i = int(number)
            if i > len(quotes[name]):
                await ctx.send("user doesn't have that many quotes...")
                return
            quote = quotes[name][i-1]
            await ctx.send("'{0}' ~{1}".format(quote,name))
        except Exception:
            await ctx.send("Third parameter must either be left out, 'all' or a number!")



#
# --------------- CHESS COMMANDS ---------------
#
@bot.command()
async def challenge(ctx, name: str):
    """challenge another player to a game of chess"""
    if len(ctx.message.mentions) > 0:
        p1 = ctx.message.author
        p2 = ctx.message.mentions[0]
        msg = '{0}, {1} challenges you to a game of chess!'.format(p2.mention, p1.mention)
        msg += '\nSo are you gonna accept like the *fearless grandmaster* you are, or chicken out? :triumph:\n\n'
        msg += 'chess.com stats:\n'
        if p1.name not in name_mapping.keys():
            msg += '{0} has not connected his chess.com username yet! :open_mouth:\n\n'.format(p1.mention)
        else:
            msg +=  '**' + p1.nick + '**\n'
            r = get_player_stats(name_mapping[p1.name])
            for n in ['bullet','blitz','rapid','daily']:
                try:
                    rating = r.json['stats']["chess_"+n]['last']['rating']
                    msg += n+": "+str(rating)+"\n"
                except Exception:
                    msg += n+": unrated\n"
            msg += '\n'
        if p2.name not in name_mapping.keys():
            msg += '{0} has not connected his chess.com username yet! :open_mouth:\n\n'.format(p2.mention)
        else:
            msg += '**' + p2.nick + '**\n'
            r = get_player_stats(name_mapping[p2.name])
            for n in ['bullet','blitz','rapid','daily']:
                try:
                    rating = r.json['stats']["chess_"+n]['last']['rating']
                    msg += n+": "+str(rating)+"\n"
                except Exception:
                    msg += n+": unrated\n"
            msg += '\n'
        await ctx.send(msg)
    else:
        await ctx.send("Please tag the player you want to challenge!")


@bot.command(aliases=['rating'])
async def chessdotcom(ctx, name: str):
    """Get chess.com stats and info about this player"""
    try:

        if len(ctx.message.mentions) > 0:
            print(name)
            print(ctx.message.mentions)
            if ctx.message.mentions[0].name in name_mapping.keys():
                name = name_mapping[ctx.message.mentions[0].name]
            else:
                await ctx.send("This user hasn't saved his chess.com username yet!")
                return
        r = get_player_stats(name)
        stat_msg = []
        msg = "Chess.com stats for " + name + "\n"
        for n in ['bullet','blitz','rapid','daily']:
            try:
                rating = r.json['stats']["chess_"+n]['last']['rating']
                msg += n+": "+str(rating)+"\n"
            except Exception:
                msg += n+": unrated\n"
        await ctx.send(msg)
    except Exception as e:
        print("E:" + str(e))
        print(Exception)
        await ctx.send("There is no chess.com user with that username!")


@bot.command(name="username")
async def save_username(ctx, name: str):
    """save your chess.com username"""
    name_mapping[ctx.message.author.name] = name
    with open('data.json', 'w') as f:
         json.dump(data, f)
         f.close()
    await ctx.send('chess.com username saved!')


# # implement winrate etc for chessdotcom stats
# client.get_player_stats('isThisLlCHESS').json['stats']['chess_daily']['record']

# # Leaderboard
# # example
# r = client.get_tournament_round_group_details('rapid-101-2191510',2,1)
# l = r.json['tournament_round_group']['players']
# print(l)

#
# --------------- ASVZ BOT COMMANDS ---------------
#
# how to handle the user login data? make it so only I can use the command and credentials are saved on pi? or make it so that others can signup as well?

# add id, lesson num, time to signups_list
# add cronjob for id
@bot.group()
async def asvz(ctx):
    """automatically sign up for asvz lessons."""
    if ctx.message.author.id != 237562253761708032:
        await ctx.send("That's not for you, you son of a monkey! (Command not yet implemented for the rest).")
        return
    if ctx.invoked_subcommand == None:
        await ctx.send("Must specify a subcommand!")

@asvz.command(name='start')
async def _start(ctx, lesson_num, frequency="weekly"):
    """signup for a specific asvz lesson, one-time or on a weekly basis"""
    if ctx.message.author.id != 237562253761708032:
        await ctx.send("You're not david, you son of a monkey! (Command not yet implemented for the rest).")
        return

    if frequency=="one-time":
        try:
            await ctx.send("Signup in progress...")
            asvz_signup(['--raspbian'],lesson_num,os.getenv("ETHZUSERNAME"),os.getenv("ETHZPASSWORD"))
            await ctx.send("Signup completed successfully! Please check yourself whether you got a spot or not.")
        except Exception as e:
            await ctx.send(f"Error during signup: \n {str(e)}")
        return 



    BOT_PATH = os.getenv("BOT_PATH")

    # TODO: make sure event/signup is not in the past

    # get starttime of the signup for the lesson
    driver = get_driver(['--raspbian'])
    st_strings = get_signup_time(lesson_num,driver).split(' ') # min hour day month year weekday
    st = []
    for el in st_strings:
        try:
            st.append(int(el))
        except:
            st.append(el)
    weekday = st[5]

    # subtract x minuts from starttime, at this time the command to run the signup bot will be executed
    timedelta_minutes_before = 6
    t = datetime.datetime(minute=st[0],hour=st[1],day=st[2],month=st[3],year=st[4])
    d = datetime.timedelta(minutes=timedelta_minutes_before)
    starttime = t-d

    if t + datetime.timedelta(days=1) <= datetime.datetime.now():
        await ctx.send("This event is in the past!")
        return

    # add new id,lesson_num to signups_list
    try:
        with open(f'{BOT_PATH}signups_list','a') as f:
            id = len(f.readlines())-1 
            f.write(f'{id},{lesson_num}\n')
    except:
        with open(f'{BOT_PATH}signups_list','w+') as f:
            f.write('id,lesson_num')
            id = 0
            f.write(f'{id},{lesson_num}\n')

    # create and start cronjob
    cronjob = f'(crontab -l 2>/dev/null; echo "{starttime.minute} {starttime.hour} * * {weekday} python3 {BOT_PATH}signup_script.py {id} --raspbian") | crontab -'
    os.system(cronjob)

    await ctx.send(f"Automatic signup for lesson {lesson_num} started.")

    
@asvz.command(name='stop')
async def _stop(ctx, lesson_num):
    """Stop the weekly signup for a specific lesson."""
    await ctx.send("Not yet implemented!")





# user can just specify number => single signup, or keyword "weekly" or smth and then bot will go to site (through lesson num) and get relationship of date to link from there

# add new entry to crontab: (crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/job -with args") | crontab -

#
# --------------- DEV COMMANDS ---------------
#
@bot.group()
async def stats(ctx):
    """Stats, mainly for developing purposes"""
    if ctx.invoked_subcommand == None:
        await _temp(ctx)
        await _latency(ctx)
        await _uptime(ctx)

@stats.command(name='temp')
async def _temp(ctx):
    """Returns the CPU Temp of the bot"""
    cpu=CPUTemperature()
    temp = str(round(cpu.temperature,1))
    await ctx.send('CPU temperature: ' + temp + '°C')


@stats.command(name='latency')
async def _latency(ctx):
    """Returns the latency of the bot"""
    ms = (datetime.datetime.utcnow() - ctx.message.created_at).microseconds / 1000

    before = datetime.datetime.now()
    await ctx.send('Latency: ' + str(int(ms)) + 'ms')
    ms2 = (datetime.datetime.now() - before).microseconds / 1000

    await ctx.send('Message delay: ' + str(int(ms2)) + 'ms')
    await ctx.send('Internal latency (discord websocket protocol): ' + str(round(bot.latency*1000,1)) + 'ms')


@stats.command(name='uptime')
async def _uptime(ctx):
    """Returns how long the bot's been running"""
    await ctx.send("Uptime: " + str(datetime.datetime.now()-running_since).split('.')[0])


#
# --------------- ADMIN COMMANDS ---------------
#
@bot.group()
@commands.has_any_role('MC','admin')
async def admin(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("chef")

@admin.command(name='insult')
async def _admin(ctx, recipient: str):
    await ctx.send("Yo {0}. ".format(recipient) + random.choice(insults))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("One or more required arguments are missing. Use $help <command> to see how to use it.")
    elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingAnyRole):
        await ctx.send("you're too weak to use this command bruh")
    else:
        print(error)
        await ctx.send("yeah uhm listen, this ain't gonna work... ($help or $help <command> if you're clueless)")





# ------------------------------
# RUN
# ------------------------------
bot.run(DISCORD_TOKEN)
