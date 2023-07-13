from discord.ext import commands
import discord

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor
from cogs.nebbies import num_suffix, get_monster_body, num_suffix

interactor = DatabaseInteractor()

class Accounts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Register user 
    @commands.command(description="Register for the game")
    async def setup(self, ctx):
        if interactor.does_user_exist(ctx.author.id):
            await ctx.send(f"You are already registered! ({ctx.author.id})")
        else:
            interactor.create_user(ctx.author.id)
            await ctx.send(f"{ctx.author.name} ({ctx.author.id}) has been registered.")
    
    # Display user stats
    @commands.command()
    async def stats(self, ctx, user:discord.Member=None):
        if user == None:
            user = ctx.author
        if interactor.does_user_exist(user.id):
            stats = interactor.get_user(user.id)
            if interactor.get_selected_monster(user.id) == "None":
                displayMonster = "None"
            else:
                monster = interactor.get_monster_info(stats['Selected_Monster'])
                displayMonster = f"{monster['Name']}\n{get_monster_body(monster['Head'], monster['Body'])}\n**TP:** {num_suffix(monster['Attack'] + monster['Defense'] + monster['Intelligence'] + monster['Speed'])}"

            
            embed = discord.Embed(color=discord.Color.purple(), title=f"{user.name}'s Stats:")
            embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="Balance:", value=f"{num_suffix(stats['Tokens'])} ↁ", inline=True)
            embed.add_field(name="Level:", value=f"{stats['Level']}", inline=True)
            embed.add_field(name="Monster:", value=f"{displayMonster}", inline=False)
            embed.add_field(name="Wins:", value=f"{stats['Wins']}", inline=True)
            embed.add_field(name="Losses:", value=f"{stats['Losses']}", inline=True)
            await ctx.send(embed=embed)
        elif user == None:
            await ctx.send("You have not registered. Please register with !!setup.")
        else:
            await ctx.send(f"That user ({user.name}) has not yet registered. They will need to register with !!setup.")

async def setup(bot):
    await bot.add_cog(Accounts(bot))

