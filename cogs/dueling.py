from cogs.nebbies import get_monster_body, num_suffix, suffix_num
from db import DatabaseInteractor
import discord
from discord.ext import commands
import time
import random

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

interactor = DatabaseInteractor()


# Class for the duel selection buttons
class duelButtons(discord.ui.View):
    def __init__(
        self,
        *,
        timeout=180,
        user,
        opponent,
        userMonster,
        opponentMonster,
        duelType,
        duelColor,
    ):
        super().__init__(timeout=timeout)

        self.duelType = duelType
        self.duelColor = duelColor

        self.user = user
        self.opponent = opponent

        self.userMonster = userMonster
        self.opponentMonster = opponentMonster

        self.userChoice = None
        self.opponentChoice = None

        self.userBlacklist = []
        self.opponentBlacklist = []

        self.userMulti = {"attack": 0, "defense": 0, "speed": 0, "intelligence": 0}
        self.opponentMulti = {"attack": 0, "defense": 0, "speed": 0, "intelligence": 0}

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

    async def duelSelector(self, move: str, interaction):
        if interaction.user.name == self.user.name:
            self.userChoice = move
            self.userBlacklist.append(move)
        elif interaction.user.name == self.opponent.name:
            self.opponentChoice = move
            self.opponentBlacklist.append(move)
        await interaction.response.edit_message(
            embed=selectionEmbed(
                self.user.display_name,
                self.opponent.display_name,
                self.userChoice,
                self.opponentChoice,
                self.round,
                embedColor=self.duelColor,
            ),
            view=self,
        )

    async def duelProcessor(self, interaction):
        time.sleep(1)

        outcome = determineLoser(self.userChoice, self.opponentChoice)
        # handle outcome logic and stats decrease
        if outcome[0] == "user":
            self.userMulti[outcome[1]] += 1
        elif outcome[0] == "opponent":
            self.opponentMulti[outcome[1]] += 1

        await interaction.edit_original_response(
            embed=outcomeEmbed(
                self.user.display_name,
                self.opponent.display_name,
                self.userChoice,
                self.opponentChoice,
                self.round,
                self.userMonster,
                self.opponentMonster,
                outcome=outcome,
                userMult=self.userMulti,
                oppMult=self.opponentMulti,
                embedColor=self.duelColor,
            ),
            view=self,
        )

        time.sleep(3)

        for child in self.children:
            child.disabled = False
        self.userChoice = None
        self.opponentChoice = None

        if self.round != 3:
            self.round += 1
            await interaction.edit_original_response(
                embed=selectionEmbed(
                    self.user.display_name,
                    self.opponent.display_name,
                    self.userChoice,
                    self.opponentChoice,
                    self.round,
                    embedColor=self.duelColor,
                ),
                view=self,
            )
        else:
            origUserStats = {
                "Attack": self.userMonster["Attack"],
                "Defense": self.userMonster["Defense"],
                "Intelligence": self.userMonster["Intelligence"],
                "Speed": self.userMonster["Speed"],
            }
            origOppStats = {
                "Attack": self.opponentMonster["Attack"],
                "Defense": self.opponentMonster["Defense"],
                "Intelligence": self.opponentMonster["Intelligence"],
                "Speed": self.opponentMonster["Speed"],
            }

            for stat, decrease in self.userMulti.items():
                self.userMonster[stat.capitalize()] *= 1 - (
                    self.DECREASE_CONSTANT * decrease
                )
            for stat, decrease in self.opponentMulti.items():
                self.opponentMonster[stat.capitalize()] *= 1 - (
                    self.DECREASE_CONSTANT * decrease
                )

            totalUser = (
                self.userMonster["Attack"]
                + self.userMonster["Defense"]
                + self.userMonster["Intelligence"]
                + self.userMonster["Speed"]
            )
            totalOpp = (
                self.opponentMonster["Attack"]
                + self.opponentMonster["Defense"]
                + self.opponentMonster["Intelligence"]
                + self.opponentMonster["Speed"]
            )

            userChance = float(totalUser / (totalUser + totalOpp))

            winner = random.random()

            if winner < userChance:
                winner = "user"
            else:
                winner = "opponent"

            await interaction.edit_original_response(
                embed=finalEmbed(
                    user=self.user.display_name,
                    opponent=self.opponent.display_name,
                    userMonster=self.userMonster,
                    opponentMonster=self.opponentMonster,
                    userMult=self.userMulti,
                    oppMult=self.opponentMulti,
                    totalUser=totalUser,
                    totalOpp=totalOpp,
                    userChance=userChance,
                    embedColor=self.duelColor,
                )
            )
            time.sleep(3)
            await interaction.edit_original_response(
                embed=resultEmbed(
                    user=self.user.display_name,
                    opponent=self.opponent.display_name,
                    userMonster=self.userMonster,
                    opponentMonster=self.opponentMonster,
                    duelType=self.duelType,
                    userChance=userChance,
                    winner=winner,
                    embedColor=self.duelColor,
                )
            )

            duelOutcome(
                winner,
                self.duelType,
                self.userMonster["ID"],
                self.opponentMonster["ID"],
                self.user.id,
                self.opponent.id,
                origUserStats,
                origOppStats,
            )

    # Selection Buttons for the duel:
    @discord.ui.button(label="Attack", style=discord.ButtonStyle.secondary, emoji="⚔️")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("attack", interaction)
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    @discord.ui.button(label="Block", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def defend(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("block", interaction)
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    @discord.ui.button(label="Outsmart", style=discord.ButtonStyle.secondary, emoji="🧠")
    async def intel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("intelligence", interaction)
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    @discord.ui.button(label="Evade", style=discord.ButtonStyle.secondary, emoji="💨")
    async def speed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("speed", interaction)
        if self.userChoice != None and self.opponentChoice != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)


# Class for duel offer buttons
class offerButtons(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        opponent: discord.Member,
        offer,
        embedColor,
        userMonster,
        opponentMonster,
    ):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.response = None
        self.opponent = opponent
        self.offer = offer
        self.embedColor = embedColor
        self.userMonster = userMonster
        self.opponentMonster = opponentMonster

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.opponent:
            await interaction.response.send_message(
                f"Only {self.opponent.display_name} can respond to the offer.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.clear_items()
        self.add_item(
            discord.ui.Button(
                label=f"Expired Duel. Use `!!{self.ctx.command}` to create a new instance",
                style=discord.ButtonStyle.gray,
                disabled=True,
            )
        )
        await self.response.edit(view=self)

    async def new_edit(self, buttonResponse, interaction: discord.Interaction):
        if buttonResponse == True:
            Embed = discord.Embed(
                title=f"{self.ctx.author.display_name} has **Accepted**",
                color=self.embedColor,
            )
            Embed.add_field(
                name="The duel will begin shortly...", value="", inline=True
            )
            await interaction.edit_original_response(embed=Embed)
            time.sleep(2)
            embed = selectionEmbed(
                self.ctx.author.display_name,
                self.opponent.display_name,
                None,
                None,
                1,
                self.embedColor,
            )
            await interaction.edit_original_response(
                embed=embed,
                view=duelButtons(
                    user=self.ctx.author,
                    opponent=self.opponent,
                    userMonster=self.userMonster,
                    opponentMonster=self.opponentMonster,
                    duelType=self.offer,
                    duelColor=self.embedColor,
                ),
            )
        else:
            Embed = discord.Embed(
                title=f"{self.ctx.author.display_name} has **Rejected**",
                color=self.embedColor,
            )
            Embed.add_field(name="***Pussy.***", value="", inline=True)
            await interaction.edit_original_response(embed=Embed)

    @discord.ui.button(label="Accept Duel", style=discord.ButtonStyle.green)
    async def YesButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()  # makes all buttons disabled until new response
        await self.new_edit(True, interaction)

    @discord.ui.button(label="Reject Duel", style=discord.ButtonStyle.red)
    async def NoButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()  # makes all buttons disabled until new response
        await self.new_edit(False, interaction)


# Command to duel another player
class Dueling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def duel(self, ctx, offer, opponent: discord.Member = None):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("You are not signed up! Type `!!setup` to start playing.")
        elif ctx.author.id == opponent.id:
            await ctx.send("You cannot duel yourself.")
        elif opponent is None or not interactor.does_user_exist(opponent.id):
            await ctx.send(
                "That user is not signed up. Please tell them to register with `!!setup`."
            )
        elif offer not in ("kill", "steal", "absorb"):
            await ctx.send(
                "Incorrect command usage. Correct command usage: !!duel `kill/steal/absorb` `user`"
            )
        elif interactor.get_selected_monster(ctx.author.id) == "None":
            await ctx.send(
                "You do not have a monster selected. Select a monster through `!!select (name)`."
            )
        elif interactor.get_selected_monster(opponent.id) == "None":
            await ctx.send(
                "Your opponent does not have a monster selected. They need to select a monster through `!!select (name)`."
            )
            """ assign into database in order to save data (self only saves locally)
        elif ctx.author.id in self.inDuel or opponent.id in self.inDuel:
            await ctx.send(
                "You or your opponent are already in a duel! Wait for the ongoing duel to finish."
            )
        """
        else:
            userMonster = interactor.get_monster_info(
                interactor.get_selected_monster(ctx.author.id)
            )
            opponentMonster = interactor.get_monster_info(
                interactor.get_selected_monster(opponent.id)
            )
            if offer == "kill":
                embedColor = 0x9A0404
            elif offer == "steal":
                embedColor = 0xF9B90B
            else:
                embedColor = 0x069D1F

            MonsterEmbed = f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Name:** {userMonster['Name']}\n**Total Power:** {num_suffix(userMonster['Attack'] + userMonster['Defense'] + userMonster['Intelligence'] + userMonster['Speed'])}\n**Attack:** {userMonster['Attack']}\n**Defense:** {userMonster['Defense']}\n**Intelligence:** {userMonster['Intelligence']}\n**Speed:** {userMonster['Speed']}"

            challenge = discord.Embed(
                title=f"{ctx.author.display_name} has challenged you to a **{offer}** duel!",
                description="Will you accept? Reply with `duel accept` or `duel deny`",
                color=embedColor,
            )
            challenge.add_field(
                name=f"{ctx.author.display_name}'s Nebby:",
                value=MonsterEmbed,
                inline=True,
            )
            challenge.add_field(name="‎", value="‎", inline=True)
            challenge.add_field(
                name=f"{opponent.display_name}'s Nebby:",
                value=MonsterEmbed,
                inline=True,
            )
            view = offerButtons(
                ctx=ctx,
                opponent=opponent,
                offer=offer,
                embedColor=embedColor,
                userMonster=userMonster,
                opponentMonster=opponentMonster,
            )
            response = await ctx.send(embed=challenge, view=view)
            view.response = response
            await view.wait()


# Embed to display pending user selection for first 3 rounds
def selectionEmbed(
    user: str, opponent: str, userC: str, opponentC: str, round: int, embedColor
):
    embed = discord.Embed(
        title=f"{user} VS {opponent} - Round {round}/3", color=embedColor
    )
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
def outcomeEmbed(
    user: str,
    opponent: str,
    userC: str,
    opponentC: str,
    round: int,
    userMonster: dict,
    opponentMonster: dict,
    outcome: tuple,
    userMult: dict,
    oppMult: dict,
    embedColor,
):
    totalUser = num_suffix(
        userMonster["Attack"]
        + userMonster["Defense"]
        + userMonster["Intelligence"]
        + userMonster["Speed"]
    )
    totalOpp = num_suffix(
        opponentMonster["Attack"]
        + opponentMonster["Defense"]
        + opponentMonster["Intelligence"]
        + opponentMonster["Speed"]
    )

    userStatLabels = {
        "attack": num_suffix(userMonster["Attack"]),
        "defense": num_suffix(userMonster["Defense"]),
        "intelligence": num_suffix(userMonster["Intelligence"]),
        "speed": num_suffix(userMonster["Speed"]),
    }
    oppStatLabels = {
        "attack": num_suffix(opponentMonster["Attack"]),
        "defense": num_suffix(opponentMonster["Defense"]),
        "intelligence": num_suffix(opponentMonster["Intelligence"]),
        "speed": num_suffix(opponentMonster["Speed"]),
    }

    for stat, decrease in userMult.items():
        userStatLabels[stat] += "🔻" * decrease
    for stat, decrease in oppMult.items():
        oppStatLabels[stat] += "🔻" * decrease

    embed = discord.Embed(
        title=f"{user} VS {opponent} - Round {round}/3", color=embedColor
    )
    embed.add_field(name=f"{user} chose:", value=f"{userC.capitalize()}", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"‎‎{opponent} chose:", value=f"‎‎{opponentC.capitalize()}", inline=True
    )

    embed.add_field(name="‎", value="‎", inline=True)

    if outcome[0] == "user":
        embed.add_field(
            name="‎",
            value=f"**{opponentMonster['Name']}** won the round with __{opponentC}__!\n\n**{userMonster['Name']}**'s __{userC}__ has been decreased.\n",
        )
    elif outcome[0] == "opponent":
        embed.add_field(
            name="‎",
            value=f"**{userMonster['Name']}** won the round with __{userC}__!\n\n**{opponentMonster['Name']}**'s __{opponentC}__ has been decreased.\n",
        )
    elif outcome[0] == "none":
        embed.add_field(
            name="‎",
            value=f"**{userMonster['Name']}** and **{opponentMonster['Name']}** chose __{userC}__ and __{opponentC}__,\n\nhaving no effect on each other.\n",
        )
    elif outcome[0] == "tie":
        embed.add_field(
            name="‎",
            value=f"Both nebbies chose **{opponentC}**,\n\nhaving no effect on each other.\n",
        )

    embed.add_field(name="‎", value="‎", inline=True)

    embed.add_field(
        name=f"{userMonster['Name']}",
        value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Total Power:** {totalUser}\n**Attack:** {userStatLabels['attack']}\n**Defense:** {userStatLabels['defense']}\n**Intelligence:** {userStatLabels['intelligence']}\n**Speed:** {userStatLabels['speed']}",
        inline=True,
    )
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"{opponentMonster['Name']}",
        value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Total Power:** {totalOpp}\n**Attack:** {oppStatLabels['attack']}\n**Defense:** {oppStatLabels['defense']}\n**Intelligence:** {oppStatLabels['intelligence']}\n**Speed:** {oppStatLabels['speed']}",
        inline=True,
    )

    return embed


# Determines loser of first 3 rounds, output[0] represents which one loses their stats, output[1] determines which stat is decreased
def determineLoser(userC, opponentC):
    if userC == opponentC:
        return ("tie", None)
    outcomes = {
        "attack": {
            "intelligence": ("opponent", opponentC),
            "defense": ("user", userC),
            "speed": ("none", userC),
        },
        "defense": {
            "attack": ("opponent", opponentC),
            "speed": ("user", userC),
            "intelligence": ("none", userC),
        },
        "speed": {
            "intelligence": ("opponent", opponentC),
            "defense": ("user", userC),
            "attack": ("none", userC),
        },
        "intelligence": {
            "speed": ("opponent", opponentC),
            "attack": ("user", userC),
            "defense": ("none", userC),
        },
    }

    if userC in outcomes and opponentC in outcomes[userC]:
        return outcomes[userC][opponentC]
    else:
        return "invalid", None


# Embed to display final round
def finalEmbed(
    user: str,
    opponent: str,
    userMonster: dict,
    opponentMonster: dict,
    userMult: dict,
    oppMult: dict,
    totalUser: int,
    totalOpp: int,
    userChance: float,
    embedColor,
):
    totalUser = num_suffix(totalUser)
    totalOpp = num_suffix(totalOpp)

    userStatLabels = {
        "attack": num_suffix(userMonster["Attack"]),
        "defense": num_suffix(userMonster["Defense"]),
        "intelligence": num_suffix(userMonster["Intelligence"]),
        "speed": num_suffix(userMonster["Speed"]),
    }
    oppStatLabels = {
        "attack": num_suffix(opponentMonster["Attack"]),
        "defense": num_suffix(opponentMonster["Defense"]),
        "intelligence": num_suffix(opponentMonster["Intelligence"]),
        "speed": num_suffix(opponentMonster["Speed"]),
    }

    for stat, decrease in userMult.items():
        userStatLabels[stat] += "🔻" * decrease
    for stat, decrease in oppMult.items():
        oppStatLabels[stat] += "🔻" * decrease

    probBar = ""
    for _ in range(round(userChance * 24)):
        probBar += "🟩"
    for _ in range(abs(round((1 - userChance) * 24))):
        probBar += "🟥"

    embed = discord.Embed(
        title=f"{user} VS {opponent} - Final Showdown", color=embedColor
    )
    embed.add_field(
        name=f"{user}:", value=f"{round(userChance * 100, 1)}% chance", inline=True
    )
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"{opponent}:",
        value=f"{'{:.1f}'.format(100 - round(userChance * 100, 1))}% chance",
        inline=True,
    )

    embed.add_field(name="‎", value=f"{probBar}", inline=False)

    embed.add_field(
        name=f"{userMonster['Name']}",
        value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Total Power:** {totalUser}\n**Attack:** {userStatLabels['attack']}\n**Defense:** {userStatLabels['defense']}\n**Intelligence:** {userStatLabels['intelligence']}\n**Speed:** {userStatLabels['speed']}",
        inline=True,
    )
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"{opponentMonster['Name']}",
        value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Total Power:** {totalOpp}\n**Attack:** {oppStatLabels['attack']}\n**Defense:** {oppStatLabels['defense']}\n**Intelligence:** {oppStatLabels['intelligence']}\n**Speed:** {oppStatLabels['speed']}",
        inline=True,
    )

    embed.set_footer(text="Determining winner...")

    return embed


# Embed to display outcome and winner of duel
def resultEmbed(
    user: str,
    opponent: str,
    userMonster: dict,
    opponentMonster: dict,
    duelType: str,
    userChance: float,
    winner: str,
    embedColor,
):
    totalUser = num_suffix(
        userMonster["Attack"]
        + userMonster["Defense"]
        + userMonster["Intelligence"]
        + userMonster["Speed"]
    )
    totalOpp = num_suffix(
        opponentMonster["Attack"]
        + opponentMonster["Defense"]
        + opponentMonster["Intelligence"]
        + opponentMonster["Speed"]
    )

    if winner == "user":
        embed = discord.Embed(
            title=f"{user} won against {opponent} with a {round(userChance * 100, 1)}% chance!",
            color=embedColor,
        )
    else:
        embed = discord.Embed(
            title=f"{opponent} won against {user} with a {'{:.1f}'.format(100 - round(userChance * 100, 1))}% chance!",
            color=embedColor,
        )

    if duelType == "kill":
        actionEmoji = "🔪"
        if winner == "user":
            embed.add_field(
                name=f"{userMonster['Name']}",
                value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Total Power:** {num_suffix(suffix_num(totalOpp) + suffix_num(totalUser))}  (+{totalOpp})\n**Attack:** {num_suffix(userMonster['Attack'] + opponentMonster['Attack'])} (+{opponentMonster['Attack']})\n**Defense:** {num_suffix(userMonster['Defense'] + opponentMonster['Defense'])} (+{opponentMonster['Defense']})\n**Intelligence:** {num_suffix(userMonster['Intelligence'] + opponentMonster['Intelligence'])} (+{opponentMonster['Intelligence']})\n**Speed:** {num_suffix(userMonster['Speed'] + opponentMonster['Speed'])} (+{opponentMonster['Speed']})",
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opponentMonster['Name']}\n(Killed)", value=f"\n:headstone:\n"
            )
        else:
            embed.add_field(
                name=f"{userMonster['Name']}\n(Killed)", value=f"\n:headstone:\n"
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opponentMonster['Name']}",
                value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Total Power:** {num_suffix(suffix_num(totalOpp) + suffix_num(totalUser))} (+{totalUser})\n**Attack:** {num_suffix(userMonster['Attack'] + opponentMonster['Attack'])} (+{userMonster['Attack']})\n**Defense:** {num_suffix(userMonster['Defense'] + opponentMonster['Defense'])} (+{userMonster['Defense']})\n**Intelligence:** {num_suffix(userMonster['Intelligence'] + opponentMonster['Intelligence'])} (+{userMonster['Intelligence']})\n**Speed:** {num_suffix(userMonster['Speed'] + opponentMonster['Speed'])} (+{userMonster['Speed']})",
            )
    elif duelType == "absorb":
        actionEmoji = "💉"
        if winner == "user":
            atkChange = int(opponentMonster["Attack"] * 0.5)
            defChange = int(opponentMonster["Defense"] * 0.5)
            spdChange = int(opponentMonster["Speed"] * 0.5)
            intlChange = int(opponentMonster["Intelligence"] * 0.5)
            totalChange = atkChange + defChange + spdChange + intlChange

            embed.add_field(
                name=f"{userMonster['Name']}",
                value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Total Power:** {num_suffix(suffix_num(totalUser) + totalChange)} (+{totalChange})\n**Attack:** {num_suffix(userMonster['Attack'] + atkChange)} (+{atkChange})\n**Defense:** {num_suffix(userMonster['Defense'] + defChange)} (+{defChange})\n**Intelligence:** {num_suffix(userMonster['Intelligence'] + intlChange)} (+{intlChange})\n**Speed:** {num_suffix(userMonster['Speed'] + spdChange)} (+{spdChange})",
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opponentMonster['Name']} (Absorbed)",
                value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Total Power:** {num_suffix(abs(suffix_num(totalOpp) - totalChange))} (-{totalChange})\n**Attack:** {num_suffix(abs(opponentMonster['Attack'] - atkChange))} (-{atkChange})\n**Defense:** {num_suffix(abs(opponentMonster['Defense'] - defChange))} (-{defChange})\n**Intelligence:** {num_suffix(abs(opponentMonster['Intelligence'] - intlChange))} (-{intlChange})\n**Speed:** {num_suffix(abs(opponentMonster['Speed'] - spdChange))} (-{spdChange})",
            )
        else:
            atkChange = int(userMonster["Attack"] * 0.5)
            defChange = int(userMonster["Defense"] * 0.5)
            spdChange = int(userMonster["Speed"] * 0.5)
            intlChange = int(userMonster["Intelligence"] * 0.5)
            totalChange = atkChange + defChange + spdChange + intlChange

            embed.add_field(
                name=f"{userMonster['Name']} (Absorbed)",
                value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Total Power:** {num_suffix(abs(suffix_num(totalUser) - totalChange))} (-{totalChange})\n**Attack:** {num_suffix(abs(userMonster['Attack'] - atkChange))} (-{atkChange})\n**Defense:** {num_suffix(abs(userMonster['Defense'] - defChange))} (-{defChange})\n**Intelligence:** {num_suffix(abs(userMonster['Intelligence'] - intlChange))} (-{intlChange})\n**Speed:** {num_suffix(abs(userMonster['Speed'] - spdChange))} (-{spdChange})",
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opponentMonster['Name']}",
                value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Total Power:** {num_suffix(suffix_num(totalOpp) + totalChange)} (+{totalChange})\n**Attack:** {num_suffix(opponentMonster['Attack'] + atkChange)} (+{atkChange})\n**Defense:** {num_suffix(opponentMonster['Defense'] + defChange)} (+{defChange})\n**Intelligence:** {num_suffix(opponentMonster['Intelligence'] + intlChange)} (+{intlChange})\n**Speed:** {num_suffix(opponentMonster['Speed'] + spdChange)} (+{spdChange})",
            )
    elif duelType == "steal":
        actionEmoji = "🗑️"
        if winner == "user":
            embed.add_field(
                name=f"{userMonster['Name']}",
                value=f"{get_monster_body(userMonster['Head'], userMonster['Body'])}\n**Total Power:** {totalUser}\n**Attack:** {userMonster['Attack']}\n**Defense:** {userMonster['Defense']}\n**Intelligence:** {userMonster['Intelligence']}\n**Speed:** {userMonster['Speed']}",
                inline=True,
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opponentMonster['Name']} (Captured)",
                value=f"\n\n🎁\n\n**Total Power:** {totalOpp}\n**Attack:** {opponentMonster['Attack']}\n**Defense:** {opponentMonster['Defense']}\n**Intelligence:** {opponentMonster['Intelligence']}\n**Speed:** {opponentMonster['Speed']}",
                inline=True,
            )
        else:
            embed.add_field(
                name=f"{userMonster['Name']} (Captured)",
                value=f"\n\n🎁\n\n**Total Power:** {totalUser}\n**Attack:** {userMonster['Attack']}\n**Defense:** {userMonster['Defense']}\n**Intelligence:** {userMonster['Intelligence']}\n**Speed:** {userMonster['Speed']}",
                inline=True,
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opponentMonster['Name']}",
                value=f"{get_monster_body(opponentMonster['Head'], opponentMonster['Body'])}\n**Total Power:** {totalOpp}\n**Attack:** {opponentMonster['Attack']}\n**Defense:** {opponentMonster['Defense']}\n**Intelligence:** {opponentMonster['Intelligence']}\n**Speed:** {opponentMonster['Speed']}\n",
                inline=True,
            )

    return embed


# Change user stats and monster stats according to end of duel
def duelOutcome(
    winner,
    duelType,
    userMonsterID,
    oppMonsterID,
    userID,
    oppID,
    origUserStats,
    origOppStats,
):
    if winner == "user":
        if duelType == "kill":
            interactor.edit_monster(
                userMonsterID,
                origUserStats["Attack"] + origOppStats["Attack"],
                origUserStats["Defense"] + origOppStats["Defense"],
                origUserStats["Speed"] + origOppStats["Speed"],
                origUserStats["Intelligence"] + origOppStats["Intelligence"],
            )
            interactor.delete_monster(oppMonsterID)
            interactor.set_selected_monster(oppID, "None")
        elif duelType == "absorb":
            interactor.edit_monster(
                userMonsterID,
                origUserStats["Attack"] + origOppStats["Attack"] * 0.5,
                origUserStats["Defense"] + origOppStats["Defense"] * 0.5,
                origUserStats["Speed"] + origOppStats["Speed"] * 0.5,
                origUserStats["Intelligence"] + origOppStats["Intelligence"] * 0.5,
            )
            interactor.edit_monster(
                oppMonsterID,
                abs(origUserStats["Attack"] - origOppStats["Attack"] * 0.5),
                abs(origUserStats["Defense"] - origOppStats["Defense"] * 0.5),
                abs(origUserStats["Speed"] - origOppStats["Speed"] * 0.5),
                abs(origUserStats["Intelligence"] - origOppStats["Intelligence"] * 0.5),
            )
        elif duelType == "steal":
            interactor.change_monster_owner(oppMonsterID, userID)
            interactor.set_selected_monster(oppID, "None")
        interactor.add_user_WL(userID, 1, 0)
        interactor.add_user_WL(oppID, 0, 1)
    else:
        if duelType == "kill":
            interactor.edit_monster(
                oppMonsterID,
                origUserStats["Attack"] + origOppStats["Attack"],
                origUserStats["Defense"] + origOppStats["Defense"],
                origUserStats["Speed"] + origOppStats["Speed"],
                origUserStats["Intelligence"] + origOppStats["Intelligence"],
            )
            interactor.delete_monster(userMonsterID)
            interactor.set_selected_monster(userID, "None")
        elif duelType == "absorb":
            interactor.edit_monster(
                oppMonsterID,
                origUserStats["Attack"] * 0.5 + origOppStats["Attack"],
                origUserStats["Defense"] * 0.5 + origOppStats["Defense"],
                origUserStats["Speed"] * 0.5 + origOppStats["Speed"],
                origUserStats["Intelligence"] * 0.5 + origOppStats["Intelligence"],
            )
            interactor.edit_monster(
                userMonsterID,
                abs(origUserStats["Attack"] * 0.5 - origOppStats["Attack"]),
                abs(origUserStats["Defense"] * 0.5 - origOppStats["Defense"]),
                abs(origUserStats["Speed"] * 0.5 - origOppStats["Speed"]),
                abs(origUserStats["Intelligence"] * 0.5 - origOppStats["Intelligence"]),
            )
        elif duelType == "steal":
            interactor.change_monster_owner(userMonsterID, oppID)
            interactor.set_selected_monster(userID, "None")
        interactor.add_user_WL(userID, 0, 1)
        interactor.add_user_WL(oppID, 1, 0)


async def setup(bot):
    await bot.add_cog(Dueling(bot))
