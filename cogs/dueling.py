import discord
from discord.ext import commands

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor

interactor = DatabaseInteractor()

class Dueling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def duel(self, ctx, offer, opponent:discord.Member=None):
        if offer not in ("kill", "steal", "absorb") or opponent == None or interactor.does_user_exist(opponent.id) != True:
            await ctx.send("Incorrect command usage. Correct command usage: !!offer `kill/steal/absorb` `user`")
        else:
            await ctx.send(embed=discord.Embed(title=f"{ctx.author.name} has challenged you to a **{offer}** duel!", description="Will you accept? Reply with `!!accept` or `!!deny`"))


async def setup(bot):
    await bot.add_cog(Dueling(bot))