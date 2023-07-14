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

# Embed to display pending user selection for first 3 rounds
def selectionEmbed(user: str, opponent: str, userC: str, opponentC: str, round: int):
    embed = discord.Embed(title=f"{user} vs {opponent} - Round {round}")
    if userC != None:
        embed.add_field(name=f"{user}", value=":white_check_mark: Selected")
    else:
        embed.add_field(name=f"{user}", value=":x: Not Selected")
    if opponentC != None:
        embed.add_field(name=f"{opponent}", value=":white_check_mark: Selected")
    else:
        embed.add_field(name=f"{opponent}", value=":x: Not Selected")
    return embed

# Embed to display outcome of each of the 3 rounds after selection
def outcomeEmbed(user: str, opponent: str, userC: str, opponentC: str, round: int, userMonster: dict, opponentMonster: dict, outcome: tuple):
    totalUser = num_suffix(userMonster['Attack'] + userMonster['Defense'] + userMonster['Intelligence'] + userMonster['Speed'])
    totalOpp = num_suffix(opponentMonster['Attack'] + opponentMonster['Defense'] + opponentMonster['Intelligence'] + opponentMonster['Speed'])

    embed = discord.Embed(title=f"{user} VS {opponent} - Round {round}")
    embed.add_field(name=f"{user} chose:", value=f"{userC.capitalize()}", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(name=f"{opponent} chose:", value=f"{opponentC.capitalize()}", inline=True)

    embed.add_field(name="‎", value="‎", inline=True)
    
    if outcome[0] == "user":
        embed.add_field(name="‎", value=f"{opponent} won the round with {opponentC}!\n\n{user}'s {userC} has been decreased.\n")
    elif outcome[0] == "opponent":
        embed.add_field(name="‎", value=f"{user} won the round with {userC}!\n\n{opponent}'s {opponentC} has been decreased.\n")
    elif outcome[0] == "none":
        embed.add_field(name="‎", value=f"{user} and {opponent} chose {userC} and {opponentC},\n\nhaving no effect on each other.\n")
    elif outcome[0] == "tie":
        embed.add_field(name="‎", value=f"Both players chose {opponentC},\n\nhaving no effect on each other.\n")

    
    embed.add_field(name="‎", value="‎", inline=True)

    embed.add_field(name=f"{userMonster['Name']}", value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Attack:** {userMonster['Attack']}\n**Defense:** {userMonster['Defense']}\n**Intelligence:** {userMonster['Intelligence']}\n**Speed:** {userMonster['Speed']}\n**Total Power:** {totalUser}", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(name=f"{opponentMonster['Name']}", value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Attack:** {opponentMonster['Attack']}\n**Defense:** {opponentMonster['Defense']}\n**Intelligence:** {opponentMonster['Intelligence']}\n**Speed:** {opponentMonster['Speed']}\n**Total Power:** {totalOpp})", inline=True)

    return embed

# Determines loser of first 3 rounds, output[0] represents which one loses their stats, output[1] determines which stat is decreased
def determineLoser(userC, opponentC):
    if userC == opponentC:
        return ("tie", None)
    outcomes = {
        "attack": {"intelligence": ("opponent", opponentC),
                   "defense": ("user", userC),
                   "speed": ("none", userC)},
        "defense": {"attack": ("opponent", opponentC),
                    "speed": ("user", userC),
                    "intelligence": ("none", userC)},
        "speed": {"intelligence": ("opponent", opponentC),
                  "defense": ("user", userC),
                  "attack": ("none", userC)},
        "intelligence": {"speed": ("opponent", opponentC),
                         "attack": ("user", userC),
                         "defense": ("none", userC)}
    }
    
    if userC in outcomes and opponentC in outcomes[userC]:
        return outcomes[userC][opponentC]
    else:
        return "invalid", None

# Embed to display final round and outcome of duel
def finalEmbed():
    pass

# Class for the duel buttons
class duelButtons(discord.ui.View):
    def __init__(self, *, timeout=180, user, opponent, userMonster, opponentMonster):
        super().__init__(timeout=timeout)

        # user and opponent objects
        self.user = user
        self.opponent = opponent

        self.userMonster = userMonster
        self.opponentMonster = opponentMonster
        
        self.userChoice = None
        self.opponentChoice = None

        self.userBlacklist = []
        self.opponentBlacklist = []

        self.userMulti = {"attack": 1, "defense": 1, "speed": 1, "intelligence": 1}
        self.opponentMulti = {"attack": 1, "defense": 1, "speed": 1, "intelligence": 1}

        self.round = 1
        self.DECREASE_CONSTANT = 0.35

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in (self.user, self.opponent):
            await interaction.response.send_message(
                f"This is not your duel! You can duel someone using the `duel` command.",
                ephemeral=True,
            )
            return False
        return True
    
    @discord.ui.button(label="Attack",style=discord.ButtonStyle.secondary, emoji="⚔️")
    async def attack(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name == self.user.name:
            self.userChoice = "attack"
            self.userBlacklist.append("attack")
        elif interaction.user.name == self.opponent.name:
            self.opponentChoice = "attack"
            self.opponentBlacklist.append("attack")

        
        if round == 1:
            await interaction.reponse.edit_message(embed=selectionEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round), view=self)
        else:
            await interaction.followup.edit_message(embed=selectionEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round), view=self)
        

        # Copy code below to other buttons
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            self.round += 1

            time.sleep(1)

            outcome = determineLoser(self.userChoice, self.opponentChoice)
            # handle outcome logic and stats decrease
            if outcome[0] == "user":
                self.userMulti[outcome[1]] -= self.DECREASE_CONSTANT
            elif outcome[1] == "opponent":
                self.opponentMulti[outcome[1]] -= self.DECREASE_CONSTANT
            
            print(self.userMulti)
            print(self.opponentMulti)

            
            await interaction.followup.edit_message(embed=outcomeEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round, self.userMonster, self.opponentMonster, outcome=outcome), wait=True, view=self)

            time.sleep(3)

            for child in self.children:
                child.disabled = False
            self.userChoice = None
            self.opponentChoice = None
            if self.round != 3:
                
                await interaction.followup.edit_message(embed=selectionEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round), view=self)
            else:
                await interaction.followup.edit_message(embed=finalEmbed())

        
    
    @discord.ui.button(label="Block",style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def defend(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name in (self.user.name, self.opponent.name):
            if interaction.user.name == self.user.name:
                self.userChoice = "defense"
                self.userBlacklist.append("defense")
            elif interaction.user.name == self.opponent.name:
                self.opponentChoice = "defense"
                self.opponentBlacklist.append("defense")
            await interaction.response.edit_message(embed=selectionEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round), view=self)
        
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            self.round += 1

            time.sleep(1)

            outcome = determineLoser(self.userChoice, self.opponentChoice)
            # handle outcome logic and stats decrease
            if outcome[0] == "user":
                self.userMulti[outcome[1]] -= self.DECREASE_CONSTANT
            elif outcome[1] == "opponent":
                self.opponentMulti[outcome[1]] -= self.DECREASE_CONSTANT
            elif outcome[1] == "none":
                pass
            
            print(self.userMulti)
            print(self.opponentMulti)
            await interaction.followup.send(embed=outcomeEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round, self.userMonster, self.opponentMonster, outcome=outcome), wait=True, view=self)

            time.sleep(3)

            for child in self.children:
                child.disabled = False
            self.userChoice = None
            self.opponentChoice = None
            if self.round != 3:
                await interaction.followup.send(embed=selectionEmbed(self.user.display_name, self.opponent.display_name, self.userChoice, self.opponentChoice, self.round), view=self)
            else:
                await interaction.followup.send(embed=finalEmbed())
    
    @discord.ui.button(label="Outsmart",style=discord.ButtonStyle.secondary, emoji="🧠")
    async def intelligence(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name == self.user.name:
            self.userChoice = "intelligence"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice, self.round), view=self)
        elif interaction.user.name == self.opponent:
            self.opponentChoice = "intelligence"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice, self.round), view=self)
    
    @discord.ui.button(label="Evade",style=discord.ButtonStyle.secondary, emoji="💨")
    async def speed(self,interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user.name == self.user.name:
            self.userChoice = "speed"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice, self.round), view=self)
        elif interaction.user.name == self.opponent:
            self.opponentChoice = "speed"
            await interaction.response.edit_message(embed=selectionEmbed(self.user, self.opponent, self.userChoice, self.opponentChoice, self.round), view=self)

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

            challenge = discord.Embed(title=f"{ctx.author.display_name} has challenged you to a **{offer}** duel!", description="Will you accept? Reply with `duel accept` or `duel deny`")
            challenge.add_field(name=f"{ctx.author.display_name}'s monster", value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Name:** {userMonster['Name']}\n**Attack:** {userMonster['Attack']}\n**Defense:** {userMonster['Defense']}\n**Intelligence:** {userMonster['Intelligence']}\n**Speed:** {userMonster['Speed']}\n**Total Power:** {num_suffix(userMonster['Attack'] + userMonster['Defense'] + userMonster['Intelligence'] + userMonster['Speed'])}", inline=True)
            challenge.add_field(name="‎", value="‎", inline=True)
            challenge.add_field(name=f"{opponent.display_name}'s monster", value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Name:** {opponentMonster['Name']}\n**Attack:** {opponentMonster['Attack']}\n**Defense:** {opponentMonster['Defense']}\n**Intelligence:** {opponentMonster['Intelligence']}\n**Speed:** {opponentMonster['Speed']}\n**Total Power:** {num_suffix(opponentMonster['Attack'] + opponentMonster['Defense'] + opponentMonster['Intelligence'] + opponentMonster['Speed'])}", inline=True)
            await ctx.send(embed=challenge)

            def opponentCheck(m):
                return m.author.id == opponent.id and m.content in ("duel accept", "duel deny")
            try:
                msg = await self.bot.wait_for('message', check=opponentCheck, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send(f"{opponent.display_name} failed to respond in time to {ctx.author.display_name}'s {offer} duel.")
                return

            if msg.content == "duel deny":
                await ctx.send(f"{opponent.display_name} has denied the duel offer.")
            else:
                await ctx.send(f"{opponent.display_name} has accepted your duel offer! Starting duel...")
                
                time.sleep(2)

                embed = discord.Embed(title=f"{ctx.author.display_name} VS {opponent.display_name} - Round 1")
                embed.add_field(name=f"{ctx.author.display_name}", value=":x: Not Selected")
                embed.add_field(name=f"{opponent.display_name}", value=":x: Not Selected")
                embed.add_field(name="‎", value="‎", inline=True)
                embed.add_field(name="", value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}")
                embed.add_field(name="", value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}")
                embed.add_field(name="‎", value="‎", inline=True)
                await ctx.send(embed=embed, view=duelButtons(user=ctx.author, opponent=opponent, userMonster=userMonster, opponentMonster=opponentMonster))
                


async def setup(bot):
    await bot.add_cog(Dueling(bot))