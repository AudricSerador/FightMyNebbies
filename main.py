import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import DatabaseInteractor

# Setup MySQL database interactor
interactor = DatabaseInteractor()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot init
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!!", intents=intents, status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="with myself"))

COGS = ("cogs.nebbies", "cogs.accounts", "cogs.dueling", "cogs.minigames", "cogs.fun", "cogs.admin")

# Load cogs
@bot.event
async def setup_hook() -> None:
    for i in COGS:
        await bot.load_extension(i)
    print("Were so back")

bot.run(TOKEN)


