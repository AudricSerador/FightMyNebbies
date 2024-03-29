from discord.ext import commands
import discord

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Returns bot latency
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(":ping_pong: Pong! {0}ms".format(round(self.bot.latency, 1)))

    # Color tier info
    @commands.command(pass_context=True)
    async def tier(self, ctx):
        embed = discord.Embed(
            title="Power Tier Colors",
            description="In this game your monsters will be classified as different colors depending on its power level:",
        )
        embed.add_field(
            name="Power Range",
            value="0 - 1k\n1k - 10k\n10k - 100k\n100k - 1m\n1m - 100m\n100m - 1b\n1b - 100b\n100b - 1t\n1t - 1qd\n1qd - 1qn",
            inline=True,
        )
        embed.add_field(
            name="Color",
            value="Grey\nGreen\nBlue\nPurple\nOrange\nRed\nYellow\nPink\nWhite\nBlack",
            inline=True,
        )
        await ctx.send(embed=embed)
    
    # Override help
    @commands.command(name='help', aliases=['h'])
    async def _help(self, ctx):
        embed = discord.Embed(title=":question: List of commands", description="New to FightMyNebbies? Start with `!!setup`", color=discord.Color.purple())

        for cog in self.bot.cogs.values():
            cog_commands = cog.get_commands()
            if cog_commands:
                commands_list = "\n".join(f"`{cmd.name}`" for cmd in cog_commands)
                embed.add_field(name=cog.qualified_name, value=f"`{commands_list}`", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
