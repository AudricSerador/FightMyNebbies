from discord.ext import commands
import discord

class Mining(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Send monsters to the mines for passive income
    @commands.command(pass_context=True)
    async def mining(self, ctx):
       await ctx.send("Mining coming soon")
    
async def setup(bot):
    await bot.add_cog(Mining(bot))