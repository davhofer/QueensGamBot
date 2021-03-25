import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import logging
import random
from datetime import datetime
from chessdotcom import get_player_stats, client
from gpiozero import CPUTemperature
import nest_asyncio
import time



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
running_since = datetime.now()

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


# ------------------------------
# COMMANDS
# ------------------------------
@bot.before_invoke
async def preprocess(ctx):
    #print("before invoke")
    f = open('commands.log','a')
    e = str(datetime.today()) + ' ' + str(datetime.now()) + '   ' + str(ctx.author) + ': ' + str(ctx.message) + '\n'
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

@cool.command(name='lukas',aliases=['Lukas','Kazar','@KazarEzClap'])
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
    await ctx.send('{0} joined on {0.joined_at}'.format(member.name))


@bot.command()
async def inspire(ctx):
    """inspires you! Sends a quote from inspirobot.me, an AI that creates "inspirational quotes" ;)"""
    msg = await ctx.send("Please be patient, image is loading...")

    if not os.system('cd inspirobot-bot && node lib/inspirobot.js 1') == 0:
            await ctx.send("download go ded, sorry :frowning:")
            return
    counter = 0
    while True:
        if counter==5:
            await ctx.send("Download error. Please try again.")
            return
        time.sleep(1)
        counter+=1
        for fname in os.listdir('./inspirobot-bot/'):
            if fname.endswith('.jpg'):
                msg.delete()
                await channel.send(file=discord.File('./inspirobot-bot/'+fname))
                #move file
                os.rename('./inspirobot-bot/'+fname,'./inspirobot-bot/img/'+fname)
                return







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


@bot.command()
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


# implement winrate etc for chessdotcom stats
client.get_player_stats('isThisLlCHESS').json['stats']['chess_daily']['record']

# Leaderboard
# example
r = client.get_tournament_round_group_details('rapid-101-2191510',2,1)
l = r.json['tournament_round_group']['players']
print(l)


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
    ms = (datetime.utcnow() - ctx.message.created_at).microseconds / 1000

    before = datetime.now()
    await ctx.send('Latency: ' + str(int(ms)) + 'ms')
    ms2 = (datetime.now() - before).microseconds / 1000

    await ctx.send('Message delay: ' + str(int(ms2)) + 'ms')


@stats.command(name='uptime')
async def _uptime(ctx):
    """Returns how long the bot's been running"""
    await ctx.send("Uptime: " + str(datetime.now()-running_since).split('.')[0])


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
