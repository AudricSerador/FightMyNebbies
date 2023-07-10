import discord 
from discord.ext import commands 
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor

interactor = DatabaseInteractor()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="tokens")
    @commands.has_permissions(administrator=True)
    async def modifyTokens(self, ctx, oper, user:discord.Member, tokens):
        if not isinstance(oper, str) or not tokens.isdigit() or oper not in ("add", "subtract", "set") or int(tokens) < 0 or user == None or tokens == None or oper == None:
            await ctx.send("Incorrect command usage. Correct usage: !!tokens `add/subtract` `user` `amount`")
        elif not interactor.does_user_exist(user.id):
            await ctx.send("User is not registered. Please register with !!setup.")
        else:
            if user == None:
                user = ctx.author
            if oper == "set":
                interactor.set_tokens(user.id, int(tokens))
                await ctx.send(f"Set {user}'s balance to {tokens}.")
            elif oper == "add":
                interactor.add_tokens(user.id, int(tokens))
                await ctx.send(f"Added {tokens} Tokens to {user}.")
            elif int(tokens) > interactor.get_user_balance(user.id):
                await ctx.send("You cannot subtract more than user's balance.")
            else:
                interactor.subtract_tokens(user.id, int(tokens))
                await ctx.send(f"Subtracted {tokens} Tokens from {user}.")
            



async def setup(bot):
    await bot.add_cog(Admin(bot))