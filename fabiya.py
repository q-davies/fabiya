import discord
from discord.ext import commands
import traceback
import random
import re

TOKEN = ""
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '+', intents=intents)
guild = None
commands = []


# dictionary with key to index mapping for commands[]
key_index = {}

member_ids = {}

class cCommand:
    def __init__(self, name):
        self.name = name

# could be a parent class if you want
# more for organization than anything else
class uCommand:
    def __init__(self, name, uc_command):
        self.name = name
        self.uc_command = uc_command

# easily accessible format for the Redirect command type
class Redirect:
    def __init__(self, key, message, channel_id):
        self.key = key
        self.message = message
        self.channel_id = channel_id

# easily accessible format for the React command type
class React:
    def __init__(self, key, message):
        self.key = key
        self.message = message

# -------- MEMBER STUFF --------
class Member:
    def __init__(self,id,balance,inventory):
        self.id = id
        self.name = bot.get_user(id)
        self.balance = balance
        self.inventory = inventory
    
    def desc(self):
        return(f"**name:** {self.name}\n**id:** {self.id}\n**fabiya-coin balance:** {self.balance}")

# -------- GENERAL USE COMMANDS --------
commands.append(cCommand("general-tips"))
@bot.command(name = "general-tips")
async def general_tips(ctx):
    await ctx.reply(f"there are two must-follow rules:\n1. separate command parameters are separated by spaces\n2. multi-word paramters must be encased in double quotes\n\t*ex: PLEASE DIE should be \"PLEASE DIE\"*")

commands.append(cCommand("lookup"))
@bot.command(name = "lookup")
async def lookup(ctx, name):
    for command in commands:
        if command.name == name:
            await ctx.reply(f"i'm afraid **{name}** is already in use :(")
            return
    await ctx.reply(f"**{name}** is not in use! you can use this name! you can use it! you!")

commands.append(cCommand("remove"))
@bot.command(name = "remove")
async def remove(ctx, name):
    found = False
    for command in commands:
        if command.name == name:
            if isinstance(command, cCommand):
                await ctx.reply("you can't remove pre-made commands :(")
                return
            else:
                commands.remove(command)
                found = True
    
    if found:
        try:
            fabiya_data = open("data\\fabiya_data.csv", "w+")
            for command in commands:
                if isinstance(command, uCommand):
                    if isinstance(command.uc_command, Redirect):
                        fabiya_data.write(f"redirect,\"{command.name}\",\"{command.uc_command.key}\",\"{command.uc_command.message}\",\"{command.uc_command.channel_id}\"\n")
                    elif isinstance(command.uc_command, React):
                        fabiya_data.write(f"react,\"{command.name}\",\"{command.uc_command.key}\",\"{command.uc_command.message}\"\n")
            fabiya_data.close()
        except:
            await ctx.reply(f"**{name}** was removed, but had an issue being removed from the database. contact zholtok!")
        await ctx.reply(f"**{name}** removed from user-created commands!")  
    else:
        await ctx.reply(f"**{name}** was not found in the database, so it wasn't removed! if this is a mistake, contact zholtok!")      

commands.append(cCommand("list-general"))
@bot.command(name = "list-general")
async def list_general(ctx):
    general_commands = []
    general_commands_list = "**general commands:**\n"
    for command in commands:
        if isinstance(command, cCommand):
            general_commands.append(command.name)
    general_commands.sort()
    for name in general_commands:
        general_commands_list = general_commands_list + f"{name}\n"
    await ctx.reply(general_commands_list)

# -------- STUFF FOR REACT --------
commands.append(cCommand("react-help"))
@bot.command(name = "react-help")
async def react_help(ctx):
    await ctx.reply(f"**+react <name> <key> <message>**\n\n**name**: the name of your command\n**key**: what keyword/s you want to respond to\n**message**: what you want fabiya to say\n\n*ex: +react chess chess \"i love chess!\"*\n\nstill stuck? try **+general-tips**!")

commands.append(cCommand("get-react-attributes"))
@bot.command(name = "get-react-attributes")
async def get_react_attributes(ctx, name):
    for command in commands:
        if isinstance(command, uCommand):
            if name == command.name and isinstance(command.uc_command, React):
                await ctx.reply(f"**{command.name}**\n\n**key**:\n{command.uc_command.key}\n**message**:\n{command.uc_command.message}")
                return
    await ctx.reply(f"no react command named **{name}** found :(")

commands.append(cCommand("list-react"))
@bot.command(name = "list-react")
async def list_react(ctx):
    react_commands = []
    react_commands_list = "**react commands:**\n"
    for command in commands:
        if isinstance(command, uCommand):
            if isinstance(command.uc_command, React):
                react_commands.append(command.name)
    react_commands.sort()
    for name in react_commands:
        react_commands_list = react_commands_list + f"{name}\n"
    if react_commands_list == "**react commands:**\n":
        await ctx.reply("no react commands to list")
    else:
        await ctx.reply(react_commands_list)

commands.append(cCommand("react"))
@bot.command(name = "react")
async def react(ctx, name, key, message):
    for command in commands:
        if name == command.name:
            await ctx.reply(f"{name} is already in use by another command :,(\nuse **+lookup <name>** to see if what you want is available!")
            return
    try:
        new_react = React(key, message)
        new_command = uCommand(name, new_react)
        commands.append(new_command)

        if commands[-1].uc_command.key in key_index:
                key_index[commands[-1].uc_command.key].append(len(commands)-1)
        else:
            key_index[commands[-1].uc_command.key] = [len(commands)-1]
        
        await ctx.reply(f"new react command **{name}** should have been created, test it out with your key!")
        
        try:
            fabiya_data = open("data\\fabiya_data.csv", "a")
            fabiya_data.write(f"react,\"{name}\",\"{key}\",\"{message}\"\n")
            fabiya_data.close()
        except:
            await ctx.reply("issue with saving this command to the database, contact zholtok!")
            return
    except:
        await ctx.reply("oh no... there's been an issue... and probably with your formatting! refer to **+react-help**!\nif everything seems good, harass zholtok.")



# -------- STUFF FOR REDIRECT --------
commands.append(cCommand("redirect-help"))
@bot.command(name = "redirect-help")
async def redirect_help(ctx):
    await ctx.reply(f"**+redirect <name> <key> <message> <channel_name>**\n\n**name**: the name of your command\n**key**: what keyword/s you want to respond to\n**message**: what you want fabiya to say, must include [CHANNEL]\n**channel_name**: the text-channel you want to redirect people to\n\n*ex: +redirect chess chess \"please only talk about this shit in [CHANNEL]\" chess*\n\nstill stuck? try **+general-tips**!")

commands.append(cCommand("get-redirect-attributes"))
@bot.command(name = "get-redirect-attributes")
async def get_recirect_attributes(ctx, name):
    for command in commands:
        if isinstance(command, uCommand):
            if name == command.name and isinstance(command.uc_command, Redirect):
                await ctx.reply(f"**{command.name}**\n\n**key**:\n{command.uc_command.key}\n**message**:\n{command.uc_command.message}\n**channel id**:\n{command.uc_command.channel_id}")
                return
    await ctx.reply(f"no redirect command named **{name}** found :(")

commands.append(cCommand("list-redirect"))
@bot.command(name = "list-redirect")
async def list_redirect(ctx):
    redirect_commands = []
    redirect_commands_list = "**redirect commands:**\n"
    for command in commands:
        if isinstance(command, uCommand):
            if isinstance(command.uc_command, Redirect):
                redirect_commands.append(command.name)
    redirect_commands.sort()
    for name in redirect_commands:
        redirect_commands_list = redirect_commands_list + f"{name}\n"
    if redirect_commands_list == "**redirect commands:**\n":
        await ctx.reply("no redirect commands to list")
    else:
        await ctx.reply(redirect_commands_list)

commands.append(cCommand("redirect"))
@bot.command(name = "redirect")
async def redirect(ctx, name, key, message, channel_name):
    for command in commands:
        if name == command.name:
            await ctx.reply(f"{name} is already in use by another command :,(\nuse **+lookup <name>** to see if what you want is available!")
            return
    try:
        channel = discord.utils.get(ctx.guild.channels, name = channel_name)
        channel_id = channel.id
        cID_substring = f"<#{channel_id}>"

        new_message = message.replace("[CHANNEL]", cID_substring)

        new_redirect = Redirect(key, new_message, channel_id)

        new_command = uCommand(name, new_redirect)
        commands.append(new_command)

        if commands[-1].uc_command.key in key_index:
                key_index[commands[-1].uc_command.key].append(len(commands)-1)
        else:
            key_index[commands[-1].uc_command.key] = [len(commands)-1]
        
        await ctx.reply(f"new redirect command **{name}** should have been created, test it out with your key in channels that aren't <#{channel.id}>!")
        
        try:
            fabiya_data = open("data\\fabiya_data.csv", "a")
            fabiya_data.write(f"redirect,\"{name}\",\"{key}\",\"{new_message}\",\"{channel_id}\"\n")
            fabiya_data.close()
        except:
            await ctx.reply("issue with saving this command to the database, contact zholtok!")
            return
    except:
        await ctx.reply("oh no... there's been an issue... and probably with your formatting! refer to **+redirect-help**!\nif everything seems good, harass zholtok.")

# -------- EVENT HANDLERS --------
@bot.event
async def on_ready():
    print(f"{bot.user} is on the hunt!")
    member_data = []

    try:
        with open("data\\fabiya_member_data.csv") as fabiya_member_data:
            member_data = fabiya_member_data.readlines()
    except:
        print("error reading file")
    
    for line in member_data:
        cells = line.split("~;")
        if len(cells) == 3:
            inventory = cells[2].split(",")
            member_ids[int(cells[0])] = Member(int(cells[0]),float(cells[1]),inventory)
    
    missed_members = []

    # check for members in a specific guild (old name for server)
    guild = bot.get_guild(0)
    # print(guild.members)
    for member in guild.members:
        id = member.id
        # print(id)
        if id not in member_ids:
            new_member = Member(id,0.0,["empty"])
            member_ids[id] = new_member
            missed_members.append(new_member)
    if len(missed_members) > 0:
        with open("data\\fabiya_member_data.csv", "a") as fabiya_member_append:
            for member in missed_members:
                inventory_string = ""
                for item in member.inventory:
                    inventory_string = inventory_string + f"{item},"
                fabiya_member_append.write(f"{member.id}~;{member.balance}~;{inventory_string[:-1]}\n")

@bot.event
async def on_member_join(member):
    id = member.id
    if id not in member_ids:
        new_member = Member(id,0.0,["empty"])
        member_ids[id] = new_member
        with open("data\\fabiya_member_data.csv", "a") as fabiya_member_append:
            fabiya_member_append.write(f"{new_member.id}~;{new_member.balance}~;{empty}\n")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        if message.content[0] != '+':
            for key in key_index:
                if key in message.content.lower():
                    key_command = commands[random.choice(key_index.get(key))]
                    if isinstance(key_command.uc_command, Redirect):
                        if key_command.uc_command.key in message.content.lower() and message.channel.id != key_command.uc_command.channel_id:
                            response = key_command.uc_command.message
                            await message.channel.send(f"{response}")
                    elif isinstance(key_command.uc_command, React):
                        if key_command.uc_command.key in message.content.lower():
                            response = key_command.uc_command.message
                            await message.channel.send(f"{response}")
    except:
        print(f"error somewhere with message {message.content}")
        traceback.print_exc()
    
    await bot.process_commands(message)

# -------- SETUP --------
def setup():
    token_arr = []
    # reading in commands / token from a file
    token_ff = ""
    try:
        with open("data\\fabiya_token.csv") as fabiya_token:
            token_arr = fabiya_token.readlines()
    except:
        print("error reading file")

    token_ff = token_arr[0].strip()

    command_data = []

    try:
        with open("data\\fabiya_command_data.csv") as fabiya_command_data:
            command_data = fabiya_command_data.readlines()
    except:
        print("error reading file")

    # FORMAT FOR CSV (IMPORTANT)
    # in general:
    #   type,"name",<other parameters>
    # for Redirect:
    #   type,"name","key","message",channel_id
    # for React:
    #   type,"name","key","message"

    for index, line in enumerate(command_data):
        cells = line.split(",\"")
        if cells[0] == "redirect":
            commands.append(uCommand(cells[1][:-1], Redirect(cells[2][:-1],cells[3][:-1],int(cells[4].strip("\n").strip("\"")))))
            if commands[-1].uc_command.key in key_index:
                key_index[commands[-1].uc_command.key].append(len(commands)-1)
            else:
                key_index[commands[-1].uc_command.key] = [len(commands)-1]
        elif cells[0] == "react":
            commands.append(uCommand(cells[1][:-1],React(cells[2][:-1],cells[3][:-2])))
            if commands[-1].uc_command.key in key_index:
                key_index[commands[-1].uc_command.key].append(len(commands)-1)
            else:
                key_index[commands[-1].uc_command.key] = [len(commands)-1]
    
    return token_ff


if __name__ == "__main__":
    TOKEN = setup()
    bot.run(TOKEN)