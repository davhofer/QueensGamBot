import discord
from discord.ext import commands
import json
import os
import logging
import random

#os.environ['DISCORD_TOKEN'] = 'ODIyMTU4MzE0MDI4MTM4NTU2.YFOMmQ.CqnUyxF0iHIDHALJmH0Os11pwP8'
with open('.env','r') as f:
    token = f.readline()
    f.close()
#token = os.getenv('DISCORD_TOKEN')


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('quotes.json') as f:
    quotes = json.load(f)
    f.close()

description = ''' Queens GamBot
'''

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

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times"""
    for i in range(times):
        await ctx.send(content)

@bot.command()
async def joined(ctx, member: discord.Member):
    """do stuff when a member joins"""
    #await ctx.send('{0.name} joined in {0.joined_at}'.format(member))
    return

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


bot.run(token)

#
# prefix = '$'
#
# class BotClient(discord.Client):
#     async def on_ready(self):
#
#
#     async def on_message(self, message):
#         if message.content.startswith(prefix):
#             command = (message.content[1:]).split(" ")
#             print('Message from {0.author}: {0.content}'.format(message))
#             #await message.channel.send('Message from {0.author}: {0.content}'.format(message))
#             #await message.channel.send(str(command))
#             if command[0] == "help":
#                 await message.channel.send("QUEENS GAMBOT :crown:\nCommands:\n$help - this is how you got here\n$author - my great and wonderful creator\n$ping - check if I'm still alive\n$q <user> <text> - add a quote for <user>\n$quote <user> <number> - get a specific quote from <user>. If no number is given, choose randomly\nmore tbd")
#             elif command[0] == "author":
#                 await message.channel.send("I created myself. Jokes on you.")
#             elif command[0] == "ping":
#                 await message.channel.send(":ping_pong: Pong!")
#             elif command[0] == "q":
#                 await message.channel.send("Doesn't work yet :(")
#                 # if len(command) < 3:
#                 #     await message.channel.send("Must provide a user and a quote!")
#                 # else:
#                 #     add_quote(command)
#             elif command[0] == "quote":
#                 await message.channel.send("Doesn't work yet :(")
#                 # if len(command) < 2:
#                 #     await message.channel.send("Must provide a user!")
#                 # else:
#                 #     await message.channel.send(get_quote(command[1]))
#             else:
#                 await message.channel.send("Invalid command!\ntype `$help` for a list of all commands.")
#
# client = BotClient()
# client.run('ODIyMTU4MzE0MDI4MTM4NTU2.YFOMmQ.EelUuGxZKSKQG100KXV4xbAEgNU')
#
#
#
# #bot commands
# class BotCommand:
#     def __init__(self,name,func,help):
#         self.name = name
#         self.run = func
#         self.help = help
#
#
#
# botc = {}
#
#
# botc["ping"] = BotCommand("ping", lambda msg: await msg.channel.send(":ping_pong: Pong!"),"$ping - check if I'm still alive")
#
# botc["author"] = BotCommand("author", lambda msg: await msg.channel.send("I created myself. Jokes on you."),"$author - my great and wonderful creator")
#
# botc["quote"]
#
# with open('quotes.json', 'w') as f:
#     json.dump(quotes, f)
#     f.close()

#await message.channel.send("QUEENS GAMBOT :crown:\nCommands:\n$help - this is how you got here\n$author - my great and wonderful creator\n$ping - check if I'm still alive\n$q <user> <text> - add a quote for <user>\n$quote <user> <number> - get a specific quote from <user>. If no number is given, choose randomly\nmore tbd")
# help_text = "QUEENS GAMBOT :crown:\nCommands:\n$help - this is how you got here"
# for key in botc.keys():
#     help_text +=  "\n"+botc[key].help
#
# botc["help"] = BotCommand("help", lambda msg: await msg.channel.send(help_text),help_text)
