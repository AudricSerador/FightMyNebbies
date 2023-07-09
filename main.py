import os
import random

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
bot = commands.Bot(command_prefix="!!", intents=intents)

COGS = ("cogs.nebbies",)
bot.phrases = ['kys', ':nerd:']

# Load cogs
@bot.event
async def setup_hook() -> None:
    for i in COGS:
        await bot.load_extension(i)
    print("Were so back")

# Register user 
@bot.command()
async def setup(ctx):
    if interactor.does_user_exist(ctx.author.id):
        await ctx.send(f"You are already registered! ({ctx.author.id})")
    else:
        interactor.create_user(ctx.author.id)
        await ctx.send(f"{ctx.author.name} ({ctx.author.id}) has been registered.")


# Display user stats
@bot.command()
async def stats(ctx):
    if interactor.does_user_exist(ctx.author.id):
        stats = interactor.get_user(ctx.author.id)

        embed = discord.Embed(color=discord.Color.purple(), title=f"{ctx.author.name}'s Stats")
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(name="Balance", value=f"{stats['Tokens']} ↁ", inline=True)
        embed.add_field(name="Level", value=f"{stats['Level']}", inline=True)
        embed.add_field(name="Monster", value="Coming Soon", inline=False)
        embed.add_field(name="Wins", value=f"{stats['Wins']}", inline=True)
        embed.add_field(name="Losses", value=f"{stats['Losses']}", inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("You have not registered. Please register with !!setup.")

# Purchase monster
@bot.command()
async def buy(ctx):
    pass

#Bruh
@bot.command()
async def bruh(ctx):
    await ctx.send(random.choice(bot.phrases))

bot.run(TOKEN)


