from discord.ext import commands
import discord
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.phrases = ["kys", ":nerd:", "who asked"]
        self.eightball = ["It is certain", "It is decidedly so", "Without a doubt", "Yes - definitely", "You may rely on it", "As I see it, yes", "Most likely," "Outlook good", "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again", "Don't count on it", "My reply is no", "Outlook not so good", "Very doubtful", "HELLLL NAH", "Yes on god no cap fr fr", "stfu"]

    # Sus
    @commands.command(pass_context=True)
    async def sus(self, ctx):
       await ctx.send("I like big balls")       

    # Bruh
    @commands.command()
    async def bruh(self, ctx):
        await ctx.send(random.choice(self.phrases)) 

    # 1984
    @commands.command(name="1984")
    async def literally(self, ctx, opponent:discord.Member=None):
        await ctx.send(f"literally 1984.") 
    
    # 8 ball
    @commands.command(name="8ball")
    async def _8ball(self, ctx):
        embed = discord.Embed(color=discord.Color.purple(), title=":8ball: 8ball says...", description=f"{random.choice(self.eightball)}")
        await ctx.send(embed=embed)
    

async def setup(bot):
    await bot.add_cog(Fun(bot))

