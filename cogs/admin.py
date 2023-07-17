import discord
from discord.ext import commands
import random

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor
from cogs.nebbies import suffix_num, num_suffix

interactor = DatabaseInteractor()


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tokens")
    @commands.has_permissions(administrator=True)
    async def modifyTokens(self, ctx, oper, user: discord.Member, token):
        tokens = suffix_num(token)
        if (
            tokens == None
            or tokens == False
            or not isinstance(oper, str)
            or oper not in ("add", "subtract", "set")
            or tokens < 0
            or user == None
        ):
            await ctx.send(
                "Incorrect command usage. Correct usage: !!tokens `add/subtract/set` `user` `amount`"
            )
        elif not interactor.does_user_exist(user.id):
            await ctx.send("User is not registered. Please register with !!setup.")
        else:
            if user == None:
                user = ctx.author
            if oper == "set":
                interactor.set_tokens(user.id, tokens)
                await ctx.send(f"Set {user}'s balance to {num_suffix(tokens)}.")
            elif oper == "add":
                interactor.add_tokens(user.id, tokens)
                await ctx.send(f"Added {num_suffix(tokens)} Tokens to {user}.")
            elif int(tokens) > interactor.get_user_balance(user.id):
                await ctx.send("You cannot subtract more than user's balance.")
            else:
                interactor.subtract_tokens(user.id, tokens)
                await ctx.send(f"Subtracted {num_suffix(tokens)} Tokens from {user}.")


async def setup(bot):
    await bot.add_cog(Admin(bot))
