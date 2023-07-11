from discord.ext import commands
import discord

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Color tier info
    @commands.command(pass_context=True)
    async def tier(self, ctx):
       desc = """In this game your monsters will be classified as different colors depending on its power level.\n"""
       embed = discord.Embed(title="Power Tier Colors", description=desc)
       await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Info(bot))