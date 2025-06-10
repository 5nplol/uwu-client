import discord
from discord.ext import commands
import os
import requests
import json
import ctypes
import colorama
import aiohttp
import asyncio

colorama.init()





# status index for changing status
current_status_index = 0

# Load config
def load_config():
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"TOKEN": "", "authorized_user_id": "", "prefix": "", "original_server_id": "", "target_server_id": ""}, f)

    with open('config.json', 'r') as f:
        return json.load(f)

# Save configuration
def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

clear_console()


version = "uwu tool beta"  # verison
status = "uwu tool v1"  # status


ctypes.windll.kernel32.SetConsoleTitleW(f"uwu client - {version} - Made By 5np")

colorama.init(autoreset=True)


RED = '\033[31m'
GREY = '\033[90m'
BLACK_BG = '\033[40m'
PURPLE = '\033[35m'
RESET = '\033[0m'

config = load_config()
TOKEN = config.get('TOKEN')
AUTHORIZED_USER_ID = config.get('authorized_user_id')
PREFIX = config.get('prefix')
original_server_id = config.get('original_server_id')
target_server_id = config.get('target_server_id')

if not TOKEN:
    TOKEN = input("Enter your token:")
    config['TOKEN'] = TOKEN
    save_config(config)

if not AUTHORIZED_USER_ID:
    AUTHORIZED_USER_ID = input("enter the accounts ID:")
    config['authorized_user_id'] = AUTHORIZED_USER_ID
    save_config(config)

if not PREFIX:
    PREFIX = input("Enter your Prefix:")
    config['prefix'] = PREFIX
    save_config(config)
# this for creating severs 1:1
if not original_server_id:
    original_server_id = input("Enter the original server ID:")
    config['original_server_id'] = original_server_id
    save_config(config)

if not target_server_id:
    target_server_id = input("Enter the target server ID:")
    config['target_server_id'] = target_server_id
    save_config(config)
    

intents = discord.Intents.default()
intents.messages = True  

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=PREFIX, self_bot=True)

def is_owner(ctx):
    return str(ctx.author.id) == str(AUTHORIZED_USER_ID)

async def change_status():
    status_list = [
        discord.Streaming(name="uwu client", url="https://twitch.tv/streamer"),
    ]
    global current_status_index

    while True:
        status = status_list[current_status_index]
        await bot.change_presence(activity=status)

        current_status_index = (current_status_index + 1) % len(status_list)
        await asyncio.sleep(600)  

@bot.event
async def on_ready():
    bot.loop.create_task(change_status())  
    print(f"Logged in as: {bot.user.name} (ID: {bot.user.id})")
    print(f"Prefix: {PREFIX}")
    print(f"Version: {version}")


    
    

@bot.command()
async def copy(ctx):
    original_serv_id, target_serv_id = get_serverid()
    original_serv = bot.get_guild(original_serv_id)
    target_guild = bot.get_guild(target_serv_id)

    if not original_serv or not target_guild:
        await ctx.send("Could not access the servers. Please check the server IDs in config")
        return

    try:
        category_mapping = {}

        
        for category in original_serv.categories:
            new_category = await target_guild.create_category(name=category.name)
            await replicate(category, new_category, target_guild)
            category_mapping[category.id] = new_category

        for category in original_serv.categories:
            sorted_channels = sorted(category.channels, key=lambda x: x.position)
            for channel in sorted_channels:
                if isinstance(channel, discord.TextChannel):
                    new_channel = await target_guild.create_text_channel(
                        name=channel.name,
                        category=category_mapping[category.id],
                        position=channel.position
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    new_channel = await target_guild.create_voice_channel(
                        name=channel.name,
                        category=category_mapping[category.id],
                        position=channel.position
                    )

                if new_channel:
                    await replicate(channel, new_channel, target_guild)

    except discord.Forbidden:
        await ctx.send("I do not have permission to create channels or categories in the target server")
    except discord.HTTPException as http_error:
        if http_error.status == 429:
            await ctx.send("Rate limit exceeded Please try again later")


def get_serverid():
    return int(config["original_server_id"]), int(config["target_server_id"])


async def replicate(source_channel, target_channel, target_guild):
    overwrites = source_channel.overwrites
    new_overwrites = {}

    for role_or_member, overwrite in overwrites.items():
        if isinstance(role_or_member, discord.Role):
            target_role = discord.utils.get(target_guild.roles, name=role_or_member.name)
            if target_role:
                new_overwrites[target_role] = overwrite

    await target_channel.edit(overwrites=new_overwrites)


@bot.command(aliases=["spamchannels"])
async def spamc(ctx, amount: int, *, message):
    await ctx.message.delete()
    for _i in range(amount):
        await ctx.send(message)


deleted_channels_count = 0

@bot.command(aliases=["delchannel", "last45np"])
async def delchannels(ctx):
    global deleted_channels_count
    deleted_channels_count = 0  
    await ctx.message.delete()

    for channel in list(ctx.guild.channels):
        try:
            await channel.delete()
            deleted_channels_count += 1  
            print(f"{PURPLE}[>]{RESET} deleted {RED}{channel}{RESET}")
        except Exception as e:
            print(f"[ERROR]: {e}")  

    
    print(f"{PURPLE}[>]{RESET}Total channels deleted: {RED}{deleted_channels_count}{RESET}")


spam_1 = 0 

@bot.command(aliases=["masschannels", "masschannel", "ctc"])
async def spamc1(ctx):
    global spam_1
    await ctx.message.delete()

    
    async def create_channel(index):
        global spam_1
        try:
            
            channel = await ctx.guild.create_text_channel(name=f"5np-is-cool-{index}")
            spam_1 += 1

            
            print(f"{PURPLE}[>]{RESET} Created channel {RED}{channel.name}{RESET}")

            
            await channel.send(f"hello 5np is cool")
        except Exception as e:
            print(f"[ERROR]: {e}")

    
    tasks = [create_channel(i) for i in range(250)]
    await asyncio.gather(*tasks)

    
    print(f"{PURPLE}[>]{RESET} Amount of channels created {RED}{spam_1}{RESET}")


role_1 = 0
@bot.command(aliases=["deleteroles"])
async def delroles(ctx):
    global role_1
    await ctx.message.delete()
    for role in list(ctx.guild.roles):
        try:
            await role.delete()
            role_1 += 1
            print(f"{PURPLE}[>]{RESET} deleted {RED}{role}{RESET}")
        except Exception as e:
            await ctx.send(f'[ERROR]: {e}')
            print(f"{PURPLE}[>]{RESET} amount of roles deleted {RED}{role_1}{RESET}")

@bot.command()
async def bye(ctx):
    guild = ctx.guild
    channels = guild.channels
    global deleted_channels_count

    
    delete_tasks = []
    for channel in channels:
        delete_tasks.append(channel.delete())
        deleted_channels_count += 1  
        print(f"{PURPLE}[>]{RESET} deleted {RED}{channel}{RESET}")

   
    await asyncio.gather(*delete_tasks)
    print(f"{PURPLE}[>]{RESET}Total channels deleted: {RED}{deleted_channels_count}{RESET}")



bot.run(TOKEN, bot=False)
clear_console()
