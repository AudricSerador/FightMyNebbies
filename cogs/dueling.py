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
        op,
        usMon,
        opMon,
        duelType,
        duelColor,
    ):
        super().__init__(timeout=timeout)

        self.duelType = duelType
        self.duelColor = duelColor

        self.user = user
        self.op = op

        self.usMon = usMon
        self.opMon = opMon

        self.userChoice = None
        self.opponentChoice = None

        self.userBlacklist = []
        self.opponentBlacklist = []

        self.userMulti = {"attack": 0, "defense": 0, "speed": 0, "intelligence": 0}
        self.opponentMulti = {"attack": 0, "defense": 0, "speed": 0, "intelligence": 0}

        self.round = 1
        self.DECREASE_CONSTANT = 0.35

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in (self.user, self.op):
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
        elif interaction.user.name == self.op.name:
            self.opponentChoice = move
            self.opponentBlacklist.append(move)
        await interaction.response.edit_message(
            embed=selectionEmbed(
                self.user.display_name,
                self.op.display_name,
                self.userChoice,
                self.opponentChoice,
                self.round,
                shade=self.duelColor,
            ),
            view=self,
        )

    async def duelProcessor(self, interaction):
        time.sleep(1)

        outcome = determineLoser(self.userChoice, self.opponentChoice)
        # handle outcome logic and stats decrease
        if outcome[0] == "user":
            self.userMulti[outcome[1]] += 1
        elif outcome[0] == "op":
            self.opponentMulti[outcome[1]] += 1

        await interaction.edit_original_response(
            embed=outcomeEmbed(
                self.user.display_name,
                self.op.display_name,
                self.userChoice,
                self.opponentChoice,
                self.round,
                self.usMon,
                self.opMon,
                outcome=outcome,
                userMult=self.userMulti,
                oppMult=self.opponentMulti,
                shade=self.duelColor,
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
                    self.op.display_name,
                    self.userChoice,
                    self.opponentChoice,
                    self.round,
                    shade=self.duelColor,
                ),
                view=self,
            )
        else:
            origUserStats = {
                "Attack": self.usMon["Attack"],
                "Defense": self.usMon["Defense"],
                "Intelligence": self.usMon["Intelligence"],
                "Speed": self.usMon["Speed"],
            }
            origOppStats = {
                "Attack": self.opMon["Attack"],
                "Defense": self.opMon["Defense"],
                "Intelligence": self.opMon["Intelligence"],
                "Speed": self.opMon["Speed"],
            }

            for stat, decrease in self.userMulti.items():
                self.usMon[stat.capitalize()] *= 1 - (self.DECREASE_CONSTANT * decrease)
            for stat, decrease in self.opponentMulti.items():
                self.opMon[stat.capitalize()] *= 1 - (self.DECREASE_CONSTANT * decrease)

            sumUser = (
                self.usMon["Attack"]
                + self.usMon["Defense"]
                + self.usMon["Intelligence"]
                + self.usMon["Speed"]
            )
            sumOp = (
                self.opMon["Attack"]
                + self.opMon["Defense"]
                + self.opMon["Intelligence"]
                + self.opMon["Speed"]
            )

            userChance = float(sumUser / (sumUser + sumOp))

            winner = random.random()

            if winner < userChance:
                winner = "user"
            else:
                winner = "op"

            await interaction.edit_original_response(
                embed=finalEmbed(
                    user=self.user.display_name,
                    op=self.op.display_name,
                    usMon=self.usMon,
                    opMon=self.opMon,
                    userMult=self.userMulti,
                    oppMult=self.opponentMulti,
                    sumUser=sumUser,
                    sumOp=sumOp,
                    userChance=userChance,
                    shade=self.duelColor,
                )
            )
            time.sleep(3)
            await interaction.edit_original_response(
                embed=resultEmbed(
                    user=self.user.display_name,
                    op=self.op.display_name,
                    usMon=self.usMon,
                    opMon=self.opMon,
                    duelType=self.duelType,
                    userChance=userChance,
                    winner=winner,
                    shade=self.duelColor,
                )
            )

            duelOutcome(
                winner,
                self.duelType,
                self.usMon["ID"],
                self.opMon["ID"],
                self.user.id,
                self.op.id,
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
        op: discord.Member,
        offer,
        shade,
        usMon,
        opMon,
    ):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.response = None
        self.op = op
        self.offer = offer
        self.shade = shade
        self.usMon = usMon
        self.opMon = opMon

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.op:
            await interaction.response.send_message(
                f"Only {self.op.display_name} can respond to the offer.",
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
                color=self.shade,
            )
            Embed.add_field(
                name="The duel will begin shortly...", value="", inline=True
            )
            await interaction.edit_original_response(embed=Embed, view=None)
            time.sleep(2)
            embed = selectionEmbed(
                self.ctx.author.display_name,
                self.op.display_name,
                None,
                None,
                1,
                self.shade,
            )
            await interaction.edit_original_response(
                embed=embed,
                view=duelButtons(
                    user=self.ctx.author,
                    op=self.op,
                    usMon=self.usMon,
                    opMon=self.opMon,
                    duelType=self.offer,
                    duelColor=self.shade,
                ),
            )
        else:
            Embed = discord.Embed(
                title=f"{self.op.display_name} has **Rejected**",
                color=self.shade,
            )
            Embed.add_field(name="***Pussy.***", value="", inline=True)
            await interaction.edit_original_response(embed=Embed, view=None)

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
    async def duel(self, ctx, offer, op: discord.Member = None):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("You are not signed up! Type `!!setup` to start playing.")
        elif ctx.author.id == op.id:
            await ctx.send("You cannot duel yourself.")
        elif op is None or not interactor.does_user_exist(op.id):
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
        elif interactor.get_selected_monster(op.id) == "None":
            await ctx.send(
                "Your op does not have a monster selected. They need to select a monster through `!!select (name)`."
            )
            """ assign into database in order to save data (self only saves locally)
        elif ctx.author.id in self.inDuel or op.id in self.inDuel:
            await ctx.send(
                "You or your op are already in a duel! Wait for the ongoing duel to finish."
            )
        """
        else:
            usMon = interactor.get_monster_info(
                interactor.get_selected_monster(ctx.author.id)
            )
            opMon = interactor.get_monster_info(interactor.get_selected_monster(op.id))
            if offer == "kill":
                shade = 0x9A0404
            elif offer == "steal":
                shade = 0xF9B90B
            else:
                shade = 0x069D1F

            challenge = discord.Embed(
                title=f"{ctx.author.display_name} has challenged you to a **{offer}** duel!",
                description="Will you accept? Reply with `duel accept` or `duel deny`",
                color=shade,
            )
            challenge.add_field(
                name=f"{ctx.author.display_name}'s Nebby:",
                value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Name:** {usMon['Name']}\n**Total Power:** {num_suffix(usMon['Attack'] + usMon['Defense'] + usMon['Intelligence'] + usMon['Speed'])}\n**Attack:** {usMon['Attack']}\n**Defense:** {usMon['Defense']}\n**Intelligence:** {usMon['Intelligence']}\n**Speed:** {usMon['Speed']}",
                inline=True,
            )
            challenge.add_field(name="‎", value="‎", inline=True)
            challenge.add_field(
                name=f"{op.display_name}'s Nebby:",
                value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Name:** {opMon['Name']}\n**Total Power:** {num_suffix(opMon['Attack'] + opMon['Defense'] + opMon['Intelligence'] + opMon['Speed'])}\n**Attack:** {opMon['Attack']}\n**Defense:** {opMon['Defense']}\n**Intelligence:** {opMon['Intelligence']}\n**Speed:** {opMon['Speed']}",
                inline=True,
            )
            view = offerButtons(
                ctx=ctx,
                op=op,
                offer=offer,
                shade=shade,
                usMon=usMon,
                opMon=opMon,
            )
            response = await ctx.send(embed=challenge, view=view)
            view.response = response
            await view.wait()


# Embed to display pending user selection for first 3 rounds
def selectionEmbed(user: str, op: str, userC: str, opponentC: str, round: int, shade):
    embed = discord.Embed(title=f"{user} VS {op} - Round {round}/3", color=shade)
    if userC != None:
        embed.add_field(name=f"{user}", value=":white_check_mark: Selected")
    else:
        embed.add_field(name=f"{user}", value=":x: Not Selected")
    if opponentC != None:
        embed.add_field(name=f"{op}", value=":white_check_mark: Selected")
    else:
        embed.add_field(name=f"{op}", value=":x: Not Selected")
    return embed


# Embed to display outcome of each of the 3 rounds after selection
def outcomeEmbed(
    user: str,
    op: str,
    userC: str,
    opponentC: str,
    round: int,
    usMon: dict,
    opMon: dict,
    outcome: tuple,
    userMult: dict,
    oppMult: dict,
    shade,
):
    sumUser = num_suffix(
        usMon["Attack"] + usMon["Defense"] + usMon["Intelligence"] + usMon["Speed"]
    )
    sumOp = num_suffix(
        opMon["Attack"] + opMon["Defense"] + opMon["Intelligence"] + opMon["Speed"]
    )

    userStatLabels = {
        "attack": num_suffix(usMon["Attack"]),
        "defense": num_suffix(usMon["Defense"]),
        "intelligence": num_suffix(usMon["Intelligence"]),
        "speed": num_suffix(usMon["Speed"]),
    }
    oppStatLabels = {
        "attack": num_suffix(opMon["Attack"]),
        "defense": num_suffix(opMon["Defense"]),
        "intelligence": num_suffix(opMon["Intelligence"]),
        "speed": num_suffix(opMon["Speed"]),
    }

    for stat, decrease in userMult.items():
        userStatLabels[stat] += "🔻" * decrease
    for stat, decrease in oppMult.items():
        oppStatLabels[stat] += "🔻" * decrease

    embed = discord.Embed(title=f"{user} VS {op} - Round {round}/3", color=shade)
    embed.add_field(name=f"{user} chose:", value=f"{userC.capitalize()}", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"‎‎{op} chose:", value=f"‎‎{opponentC.capitalize()}", inline=True
    )

    embed.add_field(name="‎", value="‎", inline=True)

    if outcome[0] == "user":
        embed.add_field(
            name="‎",
            value=f"**{opMon['Name']}** won the round with __{opponentC}__!\n\n**{usMon['Name']}**'s __{userC}__ has been decreased.\n",
        )
    elif outcome[0] == "op":
        embed.add_field(
            name="‎",
            value=f"**{usMon['Name']}** won the round with __{userC}__!\n\n**{opMon['Name']}**'s __{opponentC}__ has been decreased.\n",
        )
    elif outcome[0] == "none":
        embed.add_field(
            name="‎",
            value=f"**{usMon['Name']}** and **{opMon['Name']}** chose __{userC}__ and __{opponentC}__,\n\nhaving no effect on each other.\n",
        )
    elif outcome[0] == "tie":
        embed.add_field(
            name="‎",
            value=f"Both nebbies chose **{opponentC}**,\n\nhaving no effect on each other.\n",
        )

    embed.add_field(name="‎", value="‎", inline=True)

    embed.add_field(
        name=f"{usMon['Name']}",
        value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Total Power:** {sumUser}\n**Attack:** {userStatLabels['attack']}\n**Defense:** {userStatLabels['defense']}\n**Intelligence:** {userStatLabels['intelligence']}\n**Speed:** {userStatLabels['speed']}",
        inline=True,
    )
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"{opMon['Name']}",
        value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Total Power:** {sumOp}\n**Attack:** {oppStatLabels['attack']}\n**Defense:** {oppStatLabels['defense']}\n**Intelligence:** {oppStatLabels['intelligence']}\n**Speed:** {oppStatLabels['speed']}",
        inline=True,
    )

    return embed


# Determines loser of first 3 rounds, output[0] represents which one loses their stats, output[1] determines which stat is decreased
def determineLoser(userC, opponentC):
    if userC == opponentC:
        return ("tie", None)
    outcomes = {
        "attack": {
            "intelligence": ("op", opponentC),
            "defense": ("user", userC),
            "speed": ("none", userC),
        },
        "defense": {
            "attack": ("op", opponentC),
            "speed": ("user", userC),
            "intelligence": ("none", userC),
        },
        "speed": {
            "intelligence": ("op", opponentC),
            "defense": ("user", userC),
            "attack": ("none", userC),
        },
        "intelligence": {
            "speed": ("op", opponentC),
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
    op: str,
    usMon: dict,
    opMon: dict,
    userMult: dict,
    oppMult: dict,
    sumUser: int,
    sumOp: int,
    userChance: float,
    shade,
):
    sumUser = num_suffix(sumUser)
    sumOp = num_suffix(sumOp)

    userStatLabels = {
        "attack": num_suffix(usMon["Attack"]),
        "defense": num_suffix(usMon["Defense"]),
        "intelligence": num_suffix(usMon["Intelligence"]),
        "speed": num_suffix(usMon["Speed"]),
    }
    oppStatLabels = {
        "attack": num_suffix(opMon["Attack"]),
        "defense": num_suffix(opMon["Defense"]),
        "intelligence": num_suffix(opMon["Intelligence"]),
        "speed": num_suffix(opMon["Speed"]),
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

    embed = discord.Embed(title=f"{user} VS {op} - Final Showdown", color=shade)
    embed.add_field(
        name=f"{user}:", value=f"{round(userChance * 100, 1)}% chance", inline=True
    )
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"{op}:",
        value=f"{'{:.1f}'.format(100 - round(userChance * 100, 1))}% chance",
        inline=True,
    )

    embed.add_field(name="‎", value=f"{probBar}", inline=False)

    embed.add_field(
        name=f"{usMon['Name']}",
        value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Total Power:** {sumUser}\n**Attack:** {userStatLabels['attack']}\n**Defense:** {userStatLabels['defense']}\n**Intelligence:** {userStatLabels['intelligence']}\n**Speed:** {userStatLabels['speed']}",
        inline=True,
    )
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(
        name=f"{opMon['Name']}",
        value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Total Power:** {sumOp}\n**Attack:** {oppStatLabels['attack']}\n**Defense:** {oppStatLabels['defense']}\n**Intelligence:** {oppStatLabels['intelligence']}\n**Speed:** {oppStatLabels['speed']}",
        inline=True,
    )

    embed.set_footer(text="Determining winner...")

    return embed


# Embed to display outcome and winner of duel
def resultEmbed(
    user: str,
    op: str,
    usMon: dict,
    opMon: dict,
    duelType: str,
    userChance: float,
    winner: str,
    shade,
):
    sumUser = num_suffix(
        usMon["Attack"] + usMon["Defense"] + usMon["Intelligence"] + usMon["Speed"]
    )
    sumOp = num_suffix(
        opMon["Attack"] + opMon["Defense"] + opMon["Intelligence"] + opMon["Speed"]
    )

    if winner == "user":
        embed = discord.Embed(
            title=f"{user} won against {op} with a {round(userChance * 100, 1)}% chance!",
            color=shade,
        )
    else:
        embed = discord.Embed(
            title=f"{op} won against {user} with a {'{:.1f}'.format(100 - round(userChance * 100, 1))}% chance!",
            color=shade,
        )

    if duelType == "kill":
        actionEmoji = "🔪"
        if winner == "user":
            embed.add_field(
                name=f"{usMon['Name']}",
                value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Total Power:** {num_suffix(suffix_num(sumOp) + suffix_num(sumUser))}  (+{sumOp})\n**Attack:** {num_suffix(usMon['Attack'] + opMon['Attack'])} (+{opMon['Attack']})\n**Defense:** {num_suffix(usMon['Defense'] + opMon['Defense'])} (+{opMon['Defense']})\n**Intelligence:** {num_suffix(usMon['Intelligence'] + opMon['Intelligence'])} (+{opMon['Intelligence']})\n**Speed:** {num_suffix(usMon['Speed'] + opMon['Speed'])} (+{opMon['Speed']})",
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(name=f"{opMon['Name']}\n(Killed)", value=f"\n:headstone:\n")
        else:
            embed.add_field(name=f"{usMon['Name']}\n(Killed)", value=f"\n:headstone:\n")
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opMon['Name']}",
                value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Total Power:** {num_suffix(suffix_num(sumOp) + suffix_num(sumUser))} (+{sumUser})\n**Attack:** {num_suffix(usMon['Attack'] + opMon['Attack'])} (+{usMon['Attack']})\n**Defense:** {num_suffix(usMon['Defense'] + opMon['Defense'])} (+{usMon['Defense']})\n**Intelligence:** {num_suffix(usMon['Intelligence'] + opMon['Intelligence'])} (+{usMon['Intelligence']})\n**Speed:** {num_suffix(usMon['Speed'] + opMon['Speed'])} (+{usMon['Speed']})",
            )
    elif duelType == "absorb":
        actionEmoji = "💉"
        if winner == "user":
            atkDelta = int(opMon["Attack"] * 0.5)
            defDelta = int(opMon["Defense"] * 0.5)
            spdDelta = int(opMon["Speed"] * 0.5)
            intDelta = int(opMon["Intelligence"] * 0.5)
            sumDelta = atkDelta + defDelta + spdDelta + intDelta

            embed.add_field(
                name=f"{usMon['Name']}",
                value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Total Power:** {num_suffix(suffix_num(sumUser) + sumDelta)} (+{sumDelta})\n**Attack:** {num_suffix(usMon['Attack'] + atkDelta)} (+{atkDelta})\n**Defense:** {num_suffix(usMon['Defense'] + defDelta)} (+{defDelta})\n**Intelligence:** {num_suffix(usMon['Intelligence'] + intDelta)} (+{intDelta})\n**Speed:** {num_suffix(usMon['Speed'] + spdDelta)} (+{spdDelta})",
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opMon['Name']} (Absorbed)",
                value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Total Power:** {num_suffix(abs(suffix_num(sumOp) - sumDelta))} (-{sumDelta})\n**Attack:** {num_suffix(abs(opMon['Attack'] - atkDelta))} (-{atkDelta})\n**Defense:** {num_suffix(abs(opMon['Defense'] - defDelta))} (-{defDelta})\n**Intelligence:** {num_suffix(abs(opMon['Intelligence'] - intDelta))} (-{intDelta})\n**Speed:** {num_suffix(abs(opMon['Speed'] - spdDelta))} (-{spdDelta})",
            )
        else:
            atkDelta = int(usMon["Attack"] * 0.5)
            defDelta = int(usMon["Defense"] * 0.5)
            spdDelta = int(usMon["Speed"] * 0.5)
            intDelta = int(usMon["Intelligence"] * 0.5)
            sumDelta = atkDelta + defDelta + spdDelta + intDelta

            embed.add_field(
                name=f"{usMon['Name']} (Absorbed)",
                value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Total Power:** {num_suffix(abs(suffix_num(sumUser) - sumDelta))} (-{sumDelta})\n**Attack:** {num_suffix(abs(usMon['Attack'] - atkDelta))} (-{atkDelta})\n**Defense:** {num_suffix(abs(usMon['Defense'] - defDelta))} (-{defDelta})\n**Intelligence:** {num_suffix(abs(usMon['Intelligence'] - intDelta))} (-{intDelta})\n**Speed:** {num_suffix(abs(usMon['Speed'] - spdDelta))} (-{spdDelta})",
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opMon['Name']}",
                value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Total Power:** {num_suffix(suffix_num(sumOp) + sumDelta)} (+{sumDelta})\n**Attack:** {num_suffix(opMon['Attack'] + atkDelta)} (+{atkDelta})\n**Defense:** {num_suffix(opMon['Defense'] + defDelta)} (+{defDelta})\n**Intelligence:** {num_suffix(opMon['Intelligence'] + intDelta)} (+{intDelta})\n**Speed:** {num_suffix(opMon['Speed'] + spdDelta)} (+{spdDelta})",
            )
    elif duelType == "steal":
        actionEmoji = "🗑️"
        if winner == "user":
            embed.add_field(
                name=f"{usMon['Name']}",
                value=f"{get_monster_body(usMon['Head'], usMon['Body'])}\n**Total Power:** {sumUser}\n**Attack:** {usMon['Attack']}\n**Defense:** {usMon['Defense']}\n**Intelligence:** {usMon['Intelligence']}\n**Speed:** {usMon['Speed']}",
                inline=True,
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opMon['Name']} (Captured)",
                value=f"\n\n🎁\n\n**Total Power:** {sumOp}\n**Attack:** {opMon['Attack']}\n**Defense:** {opMon['Defense']}\n**Intelligence:** {opMon['Intelligence']}\n**Speed:** {opMon['Speed']}",
                inline=True,
            )
        else:
            embed.add_field(
                name=f"{usMon['Name']} (Captured)",
                value=f"\n\n🎁\n\n**Total Power:** {sumUser}\n**Attack:** {usMon['Attack']}\n**Defense:** {usMon['Defense']}\n**Intelligence:** {usMon['Intelligence']}\n**Speed:** {usMon['Speed']}",
                inline=True,
            )
            embed.add_field(name="‎", value=f"\n\n{actionEmoji}", inline=True)
            embed.add_field(
                name=f"{opMon['Name']}",
                value=f"{get_monster_body(opMon['Head'], opMon['Body'])}\n**Total Power:** {sumOp}\n**Attack:** {opMon['Attack']}\n**Defense:** {opMon['Defense']}\n**Intelligence:** {opMon['Intelligence']}\n**Speed:** {opMon['Speed']}\n",
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
