import discord 
from discord.ext import commands 
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor

interactor = DatabaseInteractor()

class Nebbies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.heads = [":grinning:", ":smiley:", ":smile:", ":grin:"]
    
    @commands.command(pass_context=True)
    async def create(self, ctx):
        embed = discord.Embed(color=discord.Color.purple(), title="Build-a-Nebby", description="How much tokens will you sacrifice?")
        await ctx.send(embed=embed)

        def check(m):
            return m.content.isdigit() and m.channel == ctx.channel

        msg = await self.bot.wait_for('message', check=check)
        await ctx.send(msg.content)


async def setup(bot):
    await bot.add_cog(Nebbies(bot))