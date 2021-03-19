import discord
import json
import os
import logging

quotes = {}

prefix = '$'

class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

        with open('quotes.json') as f:
            quotes = json.load(f)
            f.close()

    async def on_message(self, message):
        if message.content.startswith(prefix):
            command = (message.content[1:]).split(" ")
            print('Message from {0.author}: {0.content}'.format(message))
            #await message.channel.send('Message from {0.author}: {0.content}'.format(message))
            #await message.channel.send(str(command))
            if command[0] == "help":
                await message.channel.send("QUEENS GAMBOT :crown:\nCommands:\n$help - this is how you got here\n$author - my great and wonderful creator\n$ping - check if I'm still alive\n$q <user> <text> - add a quote for <user>\n$quote <user> <number> - get a specific quote from <user>. If no number is given, choose randomly\nmore tbd")
            elif command[0] == "author":
                await message.channel.send("I created myself. Jokes on you.")
            elif command[0] == "ping":
                await message.channel.send(":ping_pong: Pong!")
            elif command[0] == "q":
                await message.channel.send("Doesn't work yet :(")
                # if len(command) < 3:
                #     await message.channel.send("Must provide a user and a quote!")
                # else:
                #     add_quote(command)
            elif command[0] == "quote":
                await message.channel.send("Doesn't work yet :(")
                # if len(command) < 2:
                #     await message.channel.send("Must provide a user!")
                # else:
                #     await message.channel.send(get_quote(command[1]))
            else:
                await message.channel.send("Invalid command!\ntype `$help` for a list of all commands.")

client = BotClient()
client.run('ODIyMTU4MzE0MDI4MTM4NTU2.YFOMmQ.EelUuGxZKSKQG100KXV4xbAEgNU')



#bot commands
class BotCommand:
    def __init__(self,name,func,help):
        self.name = name
        self.run = func
        self.help = help



botc = {}


botc["ping"] = BotCommand("ping", lambda msg: await msg.channel.send(":ping_pong: Pong!"),"$ping - check if I'm still alive")

botc["author"] = BotCommand("author", lambda msg: await msg.channel.send("I created myself. Jokes on you."),"$author - my great and wonderful creator")

botc["quote"]

with open('quotes.json', 'w') as f:
    json.dump(quotes, f)
    f.close()

#await message.channel.send("QUEENS GAMBOT :crown:\nCommands:\n$help - this is how you got here\n$author - my great and wonderful creator\n$ping - check if I'm still alive\n$q <user> <text> - add a quote for <user>\n$quote <user> <number> - get a specific quote from <user>. If no number is given, choose randomly\nmore tbd")
help_text = "QUEENS GAMBOT :crown:\nCommands:\n$help - this is how you got here"
for key in botc.keys():
    help_text +=  "\n"+botc[key].help

botc["help"] = BotCommand("help", lambda msg: await msg.channel.send(help_text),help_text)
