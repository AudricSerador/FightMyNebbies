from discord.ext import commands

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def test(self, ctx):
       await ctx.send("I like big balls")        

    async def on_message(self, message):
        print(message.content)

async def setup(bot):
    await bot.add_cog(TestCog(bot))

