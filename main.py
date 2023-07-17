import os
import sys
import traceback

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
bot = commands.Bot(
    color=discord.Color.purple(),
    command_prefix="!!",
    intents=intents,
    status=discord.Status.online,
    activity=discord.Activity(type=discord.ActivityType.playing, name="!!help"),
)

COGS = (
    "cogs.nebbies",
    "cogs.accounts",
    "cogs.dueling",
    "cogs.minigames",
    "cogs.fun",
    "cogs.admin",
    "cogs.info",
)


# Load cogs
@bot.event
async def setup_hook() -> None:
    for i in COGS:
        await bot.load_extension(i)
    print("Were so back")


@bot.event
async def on_command_error(ctx, error):
    error_titles = {
        commands.CommandOnCooldown: "Command still on cooldown:",
        commands.CommandNotFound: "Command not found:",
        commands.MissingPermissions: "You can't use that command:",
        commands.MissingRequiredArgument: "Your command has missing arguments:",
    }

    error_messages = {
        commands.CommandOnCooldown: "Please try again in `{:.2f}s`",
        commands.CommandNotFound: "Type `!!help` for a list of commands.",
        commands.MissingPermissions: "This is meant for Admins only.",
        commands.MissingRequiredArgument: "Type `!!help` for a list of commands.",
    }

    error_type = type(error)
    error_title = error_titles.get(error_type)
    error_message = error_messages.get(error_type)
    embed = discord.Embed(
        title=error_title, color=discord.Color.dark_red, description=error_message
    )
    await ctx.send(embed=embed)


bot.run(TOKEN)
