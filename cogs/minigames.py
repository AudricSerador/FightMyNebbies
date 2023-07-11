import discord
from discord.ext import commands
import random
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor

interactor = DatabaseInteractor()


class Buttons(discord.ui.View):
    answers = ["infinite games but no bacon", "no games, no bacon", "infinite games, no games, but some games, and some bacon on the side", "games, games, oh so many games, but no bacon", "infinite games but also an uncountably infinite amount of games", "no bacon but some games", "some games but also some more games with some bacon", "unlimited games but only with bacon", "no games but with some games and infinite bacon", "only just one game to your lineage", "negative bacon", "negative games", "infinite negative bacon with infinite games", "3 bacon", "17 games"]

    randAnswers = random.sample(answers, 4)   

    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)     
        

    @discord.ui.button(label=f"{randAnswers[0]}",style=discord.ButtonStyle.success)
    async def one(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label=f"{randAnswers[1]}",style=discord.ButtonStyle.success)
    async def two(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label=f"{randAnswers[2]}",style=discord.ButtonStyle.success)
    async def three(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label=f"{randAnswers[3]}",style=discord.ButtonStyle.success)
    async def four(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(view=self)

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bigquestion", pass_context=True)
    async def BigQuestion(self, ctx):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("User is not registered. Please register with !!setup.")
        else:
            embed = discord.Embed(color=discord.Color.dark_purple(), title="Iron's Big Question", description="Would you rather have...")
            await ctx.send(embed=embed, view=Buttons())
            result = random.randint(1, 4)

            def check_button(i: discord.Interaction, button):
                return i.author == ctx.author and i.message == Buttons

            interaction, button = await self.bot.wait_for('button_click', check=check_button)
            if result == 1:
                reward = int(interactor.get_user_balance(ctx.author.id) * 0.1)
                await interaction.respond(embed=discord.Embed(color=discord.Color.green(), title=":white_check_mark: CORRECT!!!!", description=f"You have won {reward} Tokens."))
                interactor.add_tokens(ctx.author.id, reward)
            else:
                await interaction.respond(embed=discord.Embed(color=discord.Color.red(), title=":x: WRONG!!!!", description="You're actually retarded"))
                
            
            

async def setup(bot):
    await bot.add_cog(Minigames(bot))