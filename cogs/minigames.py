import discord
from discord.ext import commands
from static.constants import ANSWERS
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor
from cogs.nebbies import num_suffix

interactor = DatabaseInteractor()


def questionRNG(userID):
    result = random.randint(1, 4)
    if result == 1:
        reward = int(interactor.get_user_balance(userID) * 0.01)
        interactor.add_tokens(userID, reward)
        return discord.Embed(
            color=discord.Color.green(),
            title=":white_check_mark: CORRECT!!!!",
            description=f"You have won {num_suffix(reward)} Tokens.",
        )
    else:
        return discord.Embed(
            color=discord.Color.red(),
            title=":x: WRONG!!!!",
            description="You're actually retarded",
        )


def getRandomAnswer():
    return random.choice(ANSWERS)


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180, userID):
        self.userID = userID
        super().__init__(timeout=timeout)
        self.one.label = getRandomAnswer()
        self.two.label = getRandomAnswer()
        self.three.label = getRandomAnswer()
        self.four.label = getRandomAnswer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.userID:
            await interaction.response.send_message(
                f"I DIDNT ASK YOU IDIOT",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            embed=questionRNG(self.userID), view=self
        )
        self.clear_items()

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            embed=questionRNG(self.userID), view=self
        )
        self.clear_items()

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            embed=questionRNG(self.userID), view=self
        )
        self.clear_items()

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            embed=questionRNG(self.userID), view=self
        )
        self.clear_items()


class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bigquestion", pass_context=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def BigQuestion(self, ctx):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("User is not registered. Please register with !!setup.")
        else:
            embed = discord.Embed(
                color=discord.Color.dark_purple(),
                title="Iron's Big Question",
                description="Would you rather have...",
            )
            await ctx.send(embed=embed, view=Buttons(userID=ctx.author.id))

async def setup(bot):
    await bot.add_cog(Minigames(bot))
