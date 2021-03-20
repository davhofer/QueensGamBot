import discord
from discord.ext import commands
import json
import os
import logging
import random
from datetime import datetime
from chessdotcom import get_player_stats
import nest_asyncio
nest_asyncio.apply()


with open('.env','r') as f:
    token = f.readline()
    f.close()


running_since = datetime.now()


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('quotes.json') as f:
    quotes = json.load(f)
    f.close()

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

@bot.command()
async def add(ctx, left:int, right:int):
    """Add two numbers"""
    await ctx.send(left + right)

@bot.command()
async def roll(ctx):
    """Get a random number between 0 and 100"""
    result = str(random.randint(0,100))
    await ctx.send(result)


@bot.command()
async def choose(ctx, *choices: str):
    """Choose between multiple choices"""
    await ctx.send(random.choice(choices))

# @bot.command()
# async def repeat(ctx, times: int, content='repeating...'):
#     """Repeats a message multiple times"""
#     for i in range(times):
#         await ctx.send(content)

# @bot.command()
# async def joined(ctx, member: discord.Member):
#     """do stuff when a member joins"""
#     #await ctx.send('{0.name} joined in {0.joined_at}'.format(member))
#     return

@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

@cool.command(name='david')
async def _bot(ctx):
    """Is david cool?"""
    await ctx.send('Yes, david is cool.')


@cool.command(name='lukas')
async def _bot(ctx):
    """Is lukas cool?"""
    await ctx.send('Yes, lukas is cool.')

@bot.command()
async def author(ctx):
    """The dude who wrote this"""
    await ctx.send("I created myself. Jokes on you.")

@bot.command()
async def ping(ctx):
    """Check if I'm still alive"""
    await ctx.send(":ping_pong: Pong!")



@bot.command()
async def q(ctx, name: str, *quote: str):
    """Add a quote for someone. To see quotes, use $quote"""
    if name not in quotes.keys():
        quotes[name] = [' '.join(quote)]
    else:
        quotes[name].append(' '.join(quote))
    with open('quotes.json', 'w') as f:
         json.dump(quotes, f)
         f.close()
    await ctx.send("Quote for {0} added!".format(name))


@bot.command()
async def quote(ctx, name: str, number=None):
    """Get quotes of someone. To add quotes, use $q. You can leave <number> out to get a random quote, or write 'all' to see all quotes."""
    if name not in quotes.keys():
        await ctx.send("{0} doesn't have any quotes yet!".format(name))
        return
    if number==None:
        quote = random.choice(quotes[name])
        await ctx.send("'{0}' ~{1}".format(quote,name))
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

@bot.command()
async def uptime(ctx):
    """How long the bot's been running"""
    await ctx.send("Uptime: " + str(datetime.now()-running_since))

@bot.command()
async def hi(ctx):
    """Say hi!"""
    greetings = ["Hello", "Hi", "Howdy", "Sup", "wassup", "How you doin'","What's popping"]
    msg = random.choice(greetings)+", "+ctx.message.author.mention

    await ctx.send(msg)

@bot.command()
async def chessdotcom(ctx, name: str):
    """Get chess.com stats and info about this player"""
    print(name)
    #r = get_player_stats(name)
    #print(r)
    try:
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


@bot.command(name="admin")
@commands.has_any_role('MC','admin')
async def admin_com(ctx):
    await ctx.send("You have admin privileges!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("One or more required arguments are missing. Use $help <command> to see how to use it.")
    elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingRole) or isinstance(error, commands.MissingAnyRole):
        await ctx.send("You do not have the necessary permissions to use this command!")
    else:
        print(error)
        await ctx.send("Error! :open_mouth: ")

@bot.command()
async def latency(ctx):
    """Returns the latency of the bot"""
    ms = (ctx.message.created_at - datetime.now()).microseconds / 1000
    edit = str(ctx.message.created_at - datetime.utcnow())
    answer = 'Latency is ' +str(int(float(edit.split(':')[2])*1000)) + 'ms'
    await ctx.send(str(ms))
    print(str(ms))
    #await ctx.send(str(ms))



bot.run(token)
