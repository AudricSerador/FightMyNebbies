from discord.ext import commands
import discord


class MiningButtons(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.response = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                f"This instance does not belong to you, use the `!!{self.ctx.command}` command to create your own instance.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.clear_items()
        self.add_item(
            discord.ui.Button(
                label=f"This interaction has timed out. Use\n`!!{self.ctx.command}` for a new one.",
                style=discord.ButtonStyle.gray,
                disabled=True,
            )
        )
        await self.response.edit(view=self)

    async def new_edit(self, buttonResponse, interaction: discord.Interaction):
        if buttonResponse == True:
            response = f"{self.ctx.author.display_name} has chosen Yes:"
            shade = 0x069D1F
        else:
            response = f"{self.ctx.author.display_name} has chosen No:"
            shade = 0x9A0404
        Embed = discord.Embed(title=f"Your Choice was:", color=shade)
        Embed.add_field(name=response, value="", inline=True)
        await interaction.edit_original_response(embed=Embed)

    @discord.ui.button(label="Y", style=discord.ButtonStyle.green)
    async def YesButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()  # makes the buttons disabled until new response
        # self.choice == true
        await self.new_edit(True, interaction)

    @discord.ui.button(label="N", style=discord.ButtonStyle.red)
    async def NoButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()  # makes the buttons disabled until new response
        # self.choice ==true
        await self.new_edit(False, interaction)



class Mining(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Send monsters to the mines for passive income
    @commands.command(pass_context=True)
    async def mining(self, ctx):
        await ctx.send("Mining coming soon")

    @commands.command(pass_context=True)
    async def miningChoice(self, ctx):
        Embed = discord.Embed(title=f"Pick Yes or No:", color=0xF9B90B)
        view = MiningButtons(ctx=ctx)
        response = await ctx.send(embed=Embed, view=view)
        view.response = response
        await view.wait()


async def setup(bot):
    await bot.add_cog(Mining(bot))
