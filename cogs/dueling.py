import discord
from discord.ext import commands
import time
import asyncio

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor
from cogs.nebbies import get_monster_body, num_suffix

interactor = DatabaseInteractor()

def selectionEmbed(user: str, opponent: str, userC: str, opponentC: str):
    embed = discord.Embed(title=f"{user} vs {opponent} - Round 1")
    if userC != None:
        embed.add_field(name=f"{user}", value=":white_check_mark: Selected")
    else:
        embed.add_field(name=f"{user}", value=":x: Not Selected")
    if opponentC != None:
        embed.add_field(name=f"{opponent}", value=":white_check_mark: Selected")
    else:
        embed.add_field(name=f"{opponent}", value=":x: Not Selected")
    return embed
        

# Class for the duel buttons
class duelButtons(discord.ui.View):
    def __init__(self, *, timeout=180, user, opponent, userMonster, opponentMonster):
        super().__init__(timeout=timeout)
        self.user = user
        self.opponent = opponent
        self.userMonster = userMonster
        self.opponentMonster = opponentMonster
        self.userChoice = None
        self.opponentChoice = None
    
    @discord.ui.button(label="Attack",style=discord.ButtonStyle.secondary, emoji="⚔️")
    async def attack(self,interaction:discord.Interaction, button:discord.ui.Button):
        print([self.user, self.opponent, self.userChoice, self.opponentChoice, interaction.user])
        if interaction.user.name == self.user:
            self.userChoice = "attack"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
        elif interaction.user.name == self.opponent:
            self.opponentChoice = "attack"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
        
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            
    
    @discord.ui.button(label="Defense",style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def defend(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name == self.user:
            self.userChoice = "defense"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
        elif interaction.user.name == self.opponent:
            self.opponentChoice = "defense"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
    
    @discord.ui.button(label="Intelligence",style=discord.ButtonStyle.secondary, emoji="🧠")
    async def intelligence(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name == self.user:
            self.userChoice = "intelligence"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
        elif interaction.user.name == self.opponent:
            self.opponentChoice = "intelligence"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
    
    @discord.ui.button(label="Speed",style=discord.ButtonStyle.secondary, emoji="💨")
    async def speed(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name == self.user:
            self.userChoice = "speed"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)
        elif interaction.user.name == self.opponent:
            self.opponentChoice = "speed"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice), view=self)

# Command to duel another player
class Dueling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def duel(self, ctx, offer, opponent:discord.Member=None):
        if not interactor.does_user_exist(opponent.id):
            await ctx.send("That user is not signed up. Please tell them to register with `!!setup`.")
        elif offer not in ("kill", "steal", "absorb") or opponent == None:
            await ctx.send("Incorrect command usage. Correct command usage: !!duel `kill/steal/absorb` `user`")
        elif interactor.get_selected_monster(ctx.author.id) == "None":
            await ctx.send("You do not have a monster selected. Select a monster through `!!select (name)`.")
        elif interactor.get_selected_monster(opponent.id) == "None":
            await ctx.send("Your opponent does not have a monster selected. They need to select a monster through `!!select (name)`.")
        else:
            userMonster = interactor.get_monster_info(interactor.get_selected_monster(ctx.author.id))
            opponentMonster = interactor.get_monster_info(interactor.get_selected_monster(opponent.id))

            challenge = discord.Embed(title=f"{ctx.author.name} has challenged you to a **{offer}** duel!", description="Will you accept? Reply with `duel accept` or `duel deny`")
            challenge.add_field(name=f"{ctx.author.name}'s monster", value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\nName: {userMonster['Name']}\n**Attack:** {userMonster['Attack']}\nDefense: {userMonster['Defense']}\nIntelligence: {userMonster['Intelligence']}\nSpeed: {userMonster['Speed']}\nTotal Power: {num_suffix(userMonster['Attack'] + userMonster['Defense'] + userMonster['Intelligence'] + userMonster['Speed'])}")                    
            
            await ctx.send(embed=challenge)

            def opponentCheck(m):
                return m.author.id == opponent.id and m.content in ("duel accept", "duel deny")
            try:
                msg = await self.bot.wait_for('message', check=opponentCheck, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send(f"{opponent.name} failed to respond in time to {ctx.author.name}'s {offer} duel.")
                return

            if msg.content == "duel deny":
                await ctx.send(f"{opponent.name} has denied the duel offer.")
            else:
                await ctx.send(f"{opponent.name} has accepted your duel offer! Starting duel...")
                
                time.sleep(2)

                embed = discord.Embed(title=f"{ctx.author.name} vs {opponent.name} - Round 1")
                embed.add_field(name=f"{ctx.author.name}", value=":x: Not Selected")
                embed.add_field(name=f"{opponent.name}", value=":x: Not Selected")
                embed.add_field(name="‎", value="‎", inline=True)
                embed.add_field(name="", value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}")
                embed.add_field(name="", value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}")
                embed.add_field(name="‎", value="‎", inline=True)
                await ctx.send(embed=embed, view=duelButtons(user=ctx.author.name, opponent=opponent.name, userMonster=userMonster, opponentMonster=opponentMonster))
                


async def setup(bot):
    await bot.add_cog(Dueling(bot))