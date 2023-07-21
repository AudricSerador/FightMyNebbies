from cogs.nebbies import get_monster_body
from db import DatabaseInteractor
from engineering_notation import EngNumber
import discord
from discord.ext import commands
import time
import random

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

interactor = DatabaseInteractor()

DECREASE_C = 0.35
ABSORB_C = 0.5


# Class for the duel selection buttons
class duelButtons(discord.ui.View):
    def __init__(
        self,
        *,
        timeout=180,
        user,
        op,
        userMon,
        opMon,
        duelType,
        shade,
        UserLayer,
        OpLayer,
    ):
        super().__init__(timeout=timeout)

        self.round = 1  # Current Round
        self.duelType = duelType  # Duel selection
        self.shade = shade  # Duel color from selection

        self.user = user
        self.userMon = (
            userMon  # Save original stats for damage math and final result calcualtions
        )
        self.userMulti = {
            "Attack": 0,
            "Defense": 0,
            "Speed": 0,
            "Intelligence": 0,
        }  # Matrix for Determing Stat Choice (Honestly im not 100% sure what this does)
        self.userC = None  # Choice selection from buttons
        self.UserLayer = UserLayer

        self.op = op  # same layout for opponent
        self.opMon = opMon
        self.opMulti = {"Attack": 0, "Defense": 0, "Speed": 0, "Intelligence": 0}
        self.opC = None
        self.OpLayer = OpLayer

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
            self.userC = move
        elif interaction.user.name == self.op.name:
            self.opC = move
        await interaction.response.edit_message(
            embed=self.selectionEmbed(),
            view=self,
        )

    async def duelProcessor(self, interaction):
        time.sleep(1)

        self.outcome = self.determineLoser()
        # handle outcome logic and stats decrease
        if self.outcome[0] == "user":
            self.userMulti[self.outcome[1]] += 1
        elif self.outcome[0] == "op":
            self.opMulti[self.outcome[1]] += 1

        await interaction.edit_original_response(
            embed=self.outcomeEmbed(),
            view=self,
        )

        time.sleep(3)

        for child in self.children:
            child.disabled = False
        self.userC = None
        self.opC = None

        if self.round != 3:
            self.round += 1
            await interaction.edit_original_response(
                embed=self.selectionEmbed(),
                view=self,
            )
        else:
            self.userChance = float(
                self.userMon["Total"] / (self.userMon["Total"] + self.opMon["Total"])
            )

            self.winner = random.random()

            if self.winner < self.userChance:
                self.winner = "user"
                self.winnername = self.user.display_name
                self.loser = "op"
                self.losername = self.op.display_name
            else:
                self.winner = "op"
                self.winnername = self.op.display_name
                self.loser = "user"
                self.losername = self.user.display_name

            await interaction.edit_original_response(embed=self.finalEmbed())
            time.sleep(3)
            await interaction.edit_original_response(embed=self.resultEmbed())

    # Selection Buttons for the duel:
    @discord.ui.button(label="Attack", style=discord.ButtonStyle.secondary, emoji="⚔️")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("Attack", interaction)
        if self.userC != None and self.opC != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    @discord.ui.button(label="Block", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def defend(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("Defense", interaction)
        if self.userC != None and self.opC != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    @discord.ui.button(label="Outsmart", style=discord.ButtonStyle.secondary, emoji="🧠")
    async def intel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("Intelligence", interaction)
        if self.userC != None and self.opC != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    @discord.ui.button(label="Evade", style=discord.ButtonStyle.secondary, emoji="💨")
    async def speed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.duelSelector("Speed", interaction)
        if self.userC != None and self.opC != None:
            for child in self.children:
                child.disabled = True
            await self.duelProcessor(interaction)

    # Embed to display pending user selection for first 3 rounds
    def selectionEmbed(self):
        embed = discord.Embed(
            title=f"{self.user.display_name} VS {self.op.display_name} - Round {self.round}/3",
            color=self.shade,
        )
        if self.userC != None:
            embed.add_field(
                name=f"{self.user.display_name}", value=":white_check_mark: Selected"
            )
        else:
            embed.add_field(name=f"{self.user.display_name}", value=":x: Not Selected")
        if self.opC != None:
            embed.add_field(
                name=f"{self.op.display_name}", value=":white_check_mark: Selected"
            )
        else:
            embed.add_field(name=f"{self.op.display_name}", value=":x: Not Selected")
        return embed

    # Embed to display outcome of each of the 3 rounds after selection
    def outcomeEmbed(self):
        embed = discord.Embed(
            title=f"{self.user.display_name} VS {self.op.display_name} - Round {self.round}/3",
            color=self.shade,
        )
        embed.add_field(
            name=f"{self.user.display_name} chose:",
            value=f"{self.userC}",
            inline=True,
        )
        embed.add_field(name="‎", value="‎", inline=True)
        embed.add_field(
            name=f"‎‎{self.op} chose:",
            value=f"‎‎{self.opC}",
            inline=True,
        )

        embed.add_field(name="‎", value="‎", inline=True)

        if self.outcome[0] == "user":
            embed.add_field(
                name="‎",
                value=f"**{self.opMon['Name']}** won the round with __{self.opC}__!\n\n**{self.userMon['Name']}**'s __{self.userC}__ has been decreased.\n",
            )
            self.UserLayer = self.monLayer(self.userMon, self.userC)
        elif self.outcome[0] == "op":
            embed.add_field(
                name="‎",
                value=f"**{self.userMon['Name']}** won the round with __{self.userC}__!\n\n**{self.opMon['Name']}**'s __{self.opC}__ has been decreased.\n",
            )
            self.OpLayer = self.monLayer(self.opMon, self.opC)
        elif self.outcome[0] == "none":
            embed.add_field(
                name="‎",
                value=f"**{self.userMon['Name']}** and **{self.opMon['Name']}** chose __{self.userC}__ and __{self.opC}__,\n\nhaving no effect on each other.\n",
            )
        elif self.outcome[0] == "tie":
            embed.add_field(
                name="‎",
                value=f"Both nebbies chose **{self.opC}**,\n\nhaving no effect on each other.\n",
            )

        embed.add_field(name="‎", value="‎", inline=True)

        embed.add_field(
            name=self.UserLayer[0],
            value=self.UserLayer[1],
            inline=True,
        )
        embed.add_field(name="‎", value="‎", inline=True)
        embed.add_field(
            name=self.OpLayer[0],
            value=self.OpLayer[1],
            inline=True,
        )

        return embed

    # Determines loser of first 3 rounds, output[0] represents which one loses their stats, output[1] determines which stat is decreased
    def determineLoser(self):
        if self.userC == self.opC:
            return ("tie", None)
        outcomes = {
            "Attack": {
                "Intelligence": ("op", self.opC),
                "Defense": ("user", self.userC),
                "Speed": ("none", self.userC),
            },
            "Defense": {
                "Attack": ("op", self.opC),
                "Speed": ("user", self.userC),
                "Intelligence": ("none", self.userC),
            },
            "Speed": {
                "Intelligence": ("op", self.opC),
                "Defense": ("user", self.userC),
                "Attack": ("none", self.userC),
            },
            "Intelligence": {
                "Speed": ("op", self.opC),
                "Attack": ("user", self.userC),
                "Defense": ("none", self.userC),
            },
        }

        if self.userC in outcomes and self.opC in outcomes[self.userC]:
            return outcomes[self.userC][self.opC]
        else:
            return "invalid", None

    # Embed to display final round
    def finalEmbed(self):
        probBar = ""
        for _ in range(round(self.userChance * 24)):
            probBar += "🟩"
        for _ in range(abs(round((1 - self.userChance) * 24))):
            probBar += "🟥"

        self.UserLayer = self.monLayer(self.userMon)
        self.OpLayer = self.monLayer(self.opMon)

        embed = discord.Embed(
            title=f"{self.user.display_name} VS {self.op.display_name} - Final Showdown",
            color=self.shade,
        )
        embed.add_field(
            name=f"{self.user.display_name}:",
            value=f"{round(self.userChance * 100, 1)}% chance",
            inline=True,
        )
        embed.add_field(name="‎", value="‎", inline=True)
        embed.add_field(
            name=f"{self.op.display_name}:",
            value=f"{'{:.1f}'.format(100 - round(self.userChance * 100, 1))}% chance",
            inline=True,
        )

        embed.add_field(name="‎", value=f"{probBar}", inline=False)

        embed.add_field(
            name=self.UserLayer[0],
            value=self.UserLayer[1],
            inline=True,
        )
        embed.add_field(name="‎", value="‎", inline=True)
        embed.add_field(
            name=self.UserLayer[0],
            value=self.OpLayer[1],
            inline=True,
        )

        embed.set_footer(text="Determining winner...")

        return embed

    # Embed to display outcome and winner of duel
    def resultEmbed(self):
        Statlist = ("Total", "Attack", "Defense", "Intelligence", "Speed")
        embed = discord.Embed(
            title=f"{self.winnername} won against {self.losername} with a {round(self.userChance * 100, 1)}% chance!",
            color=self.shade,
        )
        if self.duelType == "kill":
            actionEmoji = "🔪"
            if self.loser == "user":
                for i in Statlist:
                    self.opMon[i] = round(
                        self.opMon["origStats"][i] + self.userMon["origStats"][i]
                    )

                self.UserLayer[0] += " (Killed)"
                self.UserLayer[1] == ":headstone:"
                self.OpLayer[0] = self.opMon["Name"]
                self.OpLayer[
                    1  # fix display also group 0 and 1 into a signular layer
                ] = f"{get_monster_body(self.opMon['Head'], self.opMon['Body'])}\n**Total Power:** {self.userMon['Total']} *(+{self.opMon['origStat']['Total']})*\n**Attack:** {self.userMon['Attack']} *(+{self.opMon['origStat']['Attack']})*\n**Defense:** {self.userMon['Defense']} *(+{self.opMon['origStat']['Defense']})*\n**Intelligence:** {self.userMon['Intelligence']} *(+{self.opMon['origStat']['Intelligence']})*\n**Speed:** {self.userMon['Speed']} *(+{self.opMon['origStat']['Speed']})*"
                interactor.edit_monster(
                    self.opMon["user_ID"],
                    self.opMon["Attack"],
                    self.opMon["Defense"],
                    self.opMon["Speed"],
                    self.opMon["Intelligence"],
                )
                interactor.delete_monster(self.userMon)
                interactor.set_selected_monster(self.user.id, "None")
            else:
                for i in Statlist:
                    self.userMon[i] = round(
                        self.userMon["origStats"][i] + self.opMon["origStats"][i]
                    )

                self.OpLayer[0] += " (Killed)"
                self.OpLayer[1] == ":headstone:"
                self.UserLayer[0] = self.userMon["Name"]
                self.UserLayer[
                    0
                ] = f"{get_monster_body(self.userMon['Head'], self.userMon['Body'])}\n**Total Power:** {self.opMon['Total']} *(+{self.userMon['origStat']['Total']})*\n**Attack:** {self.opMon['Attack']} *(+{self.userMon['origStat']['Attack']})*\n**Defense:** {self.opMon['Defense']} *(+{self.userMon['origStat']['Defense']})*\n**Intelligence:** {self.opMon['Intelligence']} *(+{self.userMon['origStat']['Intelligence']})*\n**Speed:** {self.opMon['Speed']} *(+{self.userMon['origStat']['Speed']})*"
                interactor.edit_monster(
                    self.userMon["user_ID"],
                    self.userMon["Attack"],
                    self.userMon["Defense"],
                    self.userMon["Speed"],
                    self.userMon["Intelligence"],
                )
                interactor.delete_monster(self.opMon)
                interactor.set_selected_monster(self.op.id, "None")

        elif self.duelType == "absorb":
            actionEmoji = "💉"
            if self.loser == "user":
                for i in Statlist:
                    self.userMon[i] = round(
                        self.userMon["origStats"][i]
                        + (self.opMon["origStats"][i] * ABSORB_C)
                    )
                    self.opMon[i] = round(self.opMon["origStats"][i] * (1 - ABSORB_C))
                self.UserLayer = (
                    self.userMon["Name"],
                    f"{get_monster_body(self.userMon['Head'], self.userMon['Body'])}\n**Total Power:** {self.userMon['Total']} *(-{self.opMon['origStats']['Total'] * ABSORB_C})*\n**Attack:** {self.userMon['Attack']} *(-{self.opMon['origStats']['Attack'] * ABSORB_C})*\n**Defense:** {self.userMon['Defense']} *(-{self.opMon['origStats']['Defense'] * ABSORB_C})*\n**Intelligence:** {self.userMon['Intelligence']} *(-{self.opMon['origStats']['Intelligence'] * ABSORB_C})*\n**Speed:** {self.userMon['Speed']} *(-{self.opMon['origStats']['Speed'] * ABSORB_C})*",
                )
                self.OpLayer = (
                    self.opMon["Name"],
                    f"{get_monster_body(self.opMon['Head'], self.opMon['Body'])}\n**Total Power:** {self.opMon['Total']} *(+{self.userMon['origStats']['Total'] * ABSORB_C})*\n**Attack:** {self.opMon['Attack']} *(+{self.userMon['origStats']['Attack'] * ABSORB_C})*\n**Defense:** {self.opMon['Defense']} *(+{self.userMon['origStats']['Defense'] * ABSORB_C})*\n**Intelligence:** {self.opMon['Intelligence']} *(+{self.userMon['origStats']['Intelligence'] * ABSORB_C})*\n**Speed:** {self.opMon['Speed']} *(+{self.opMon['origStats']['Speed'] * ABSORB_C})*",
                )
                interactor.edit_monster(
                    self.opMon["user_ID"],
                    self.opMon["Attack"],
                    self.opMon["Defense"],
                    self.opMon["Speed"],
                    self.opMon["Intelligence"],
                )
                interactor.edit_monster(
                    self.userMon["user_ID"],
                    self.userMon["Attack"],
                    self.userMon["Defense"],
                    self.userMon["Speed"],
                    self.userMon["Intelligence"],
                )
            else:
                for i in Statlist:
                    self.opMon[i] = round(
                        self.opMon["origStats"][i]
                        + (self.userMon["origStats"][i] * ABSORB_C)
                    )
                    self.userMon[i] = round(
                        self.userMon["origStats"][i] * (1 - ABSORB_C)
                    )
                self.UserLayer[0] = self.opMon["Name"]
                self.OpLayer[
                    1
                ] = f"{get_monster_body(self.opMon['Head'], self.opMon['Body'])}\n**Total Power:** {self.opMon['Total']} *(-{self.userMon['origStats']['Total'] * ABSORB_C})*\n**Attack:** {self.opMon['Attack']} *(-{self.userMon['origStats']['Attack'] * ABSORB_C})*\n**Defense:** {self.opMon['Defense']} *(-{self.userMon['origStat']['Defense'] * ABSORB_C})*\n**Intelligence:** {self.opMon['Intelligence']} *(-{self.userMon['origStat']['Intelligence'] * ABSORB_C})*\n**Speed:** {self.opMon['Speed']} *(-{self.userMon['origStat']['Speed'] * ABSORB_C})*"
                self.UserLayer[
                    1
                ] = f"{get_monster_body(self.userMon['Head'], self.userMon['Body'])}\n**Total Power:** {self.userMon['Total']} *(+{self.opMon['origStats']['Total'] * ABSORB_C})*\n**Attack:** {self.userMon['Attack']} *(+{self.opMon['origStats']['Attack'] * ABSORB_C})*\n**Defense:** {self.userMon['Defense']} *(-{self.opMon['origStat']['Defense'] * ABSORB_C})*\n**Intelligence:** {self.userMon['Intelligence']} *(+{self.opMon['origStat']['Intelligence'] * ABSORB_C})*\n**Speed:** {self.userMon['Speed']} *(+{self.userMon['origStat']['Speed'] * ABSORB_C})*"
                interactor.edit_monster(
                    self.opMon["user_ID"],
                    self.opMon["Attack"],
                    self.opMon["Defense"],
                    self.opMon["Speed"],
                    self.opMon["Intelligence"],
                )
                interactor.edit_monster(
                    self.userMon["user_ID"],
                    self.userMon["Attack"],
                    self.userMon["Defense"],
                    self.userMon["Speed"],
                    self.userMon["Intelligence"],
                )

        else:
            actionEmoji = "🗑️"
            if self.loser == "user":
                self.UserLayer[0] += " (Captured)"
                interactor.change_monster_owner(self.userMon, self.op.id)
                interactor.set_selected_monster(self.user.id, "None")
            else:
                self.OpLayer[0] += " (Captured)"
                interactor.change_monster_owner(self.opMon, self.user.id)
                interactor.set_selected_monster(self.op.id, "None")

        embed.add_field(
            name=self.UserLayer[0],
            value=self.UserLayer[1],
            inline=True,
        )
        embed.add_field(name=actionEmoji, value="‎", inline=True)
        embed.add_field(
            name=self.OpLayer[0],
            value=self.OpLayer[1],
            inline=True,
        )

        return embed

    # Renders out stat and monster layer
    def monLayer(self, Mon, Stat=None):
        if Stat != None:
            Mon[Stat] = Mon[Stat] * DECREASE_C
            Mon["Total"] = (
                Mon["Attack"] + Mon["Defense"] + Mon["Intelligence"] + Mon["Speed"]
            )
            Mon["StatLabel"][
                "Total"
            ] = f"**Total Power:** {EngNumber(Mon['Total'])} *(-{EngNumber(Mon['origStats']['Total'] - Mon['Total'])})*"
            Mon["StatLabel"][
                Stat
            ] = f"**{Stat}:** {EngNumber(Mon[Stat])} *(-{EngNumber(Mon['origStats'][Stat] - Mon[Stat])})*"

        monName = Mon["Name"]
        monValue = f"{get_monster_body(Mon['Head'], Mon['Body'])}\n{Mon['StatLabel']['Total']}\n{Mon['StatLabel']['Attack']}\n{Mon['StatLabel']['Defense']}\n{Mon['StatLabel']['Intelligence']}\n{Mon['StatLabel']['Speed']}"

        return (monName, monValue)


# Class for duel offer buttons
class offerButtons(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        op: discord.Member,
        offer,
        shade,
        userMon,
        opMon,
        UserLayer,
        OpLayer,
    ):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.response = None
        self.user = ctx.author
        self.op = op
        self.offer = offer
        self.shade = shade
        self.userMon = userMon
        self.opMon = opMon
        self.UserLayer = UserLayer
        self.OpLayer = OpLayer

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
            self.userC = None
            self.opC = None
            self.round = 1
            embed = duelButtons.selectionEmbed(self)
            await interaction.edit_original_response(
                embed=embed,
                view=duelButtons(
                    user=self.ctx.author,
                    op=self.op,
                    userMon=self.userMon,
                    opMon=self.opMon,
                    duelType=self.offer,
                    shade=self.shade,
                    UserLayer=self.UserLayer,
                    OpLayer=self.OpLayer,
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
            userMon = interactor.get_monster_info(
                interactor.get_selected_monster(ctx.author.id)
            )
            opMon = interactor.get_monster_info(interactor.get_selected_monster(op.id))
            if offer == "kill":
                shade = 0x9A0404
            elif offer == "steal":
                shade = 0xF9B90B
            else:
                shade = 0x069D1F

            combatlist = [userMon, opMon]

            for i in combatlist:  # Stat and Label collection for both players
                i["origStats"] = {
                    "Total": i["Attack"]
                    + i["Defense"]
                    + i["Intelligence"]
                    + i["Speed"],
                    "Attack": i["Attack"],
                    "Defense": i["Defense"],
                    "Intelligence": i["Intelligence"],
                    "Speed": i["Speed"],
                }
                i["Total"] = i["origStats"]["Total"]
                i["StatLabel"] = {
                    "Total": f"**Total:** {EngNumber(i['Total'])}",
                    "Attack": f"**Attack:** {EngNumber(i['Attack'])}",
                    "Defense": f"**Defense:** {EngNumber(i['Defense'])}",
                    "Intelligence": f"**Intelligence:** {EngNumber(i['Intelligence'])}",
                    "Speed": f"**Speed:** {EngNumber(i['Speed'])}",
                }
            UserLayer = duelButtons.monLayer(self, userMon)
            OpLayer = duelButtons.monLayer(self, opMon)

            challenge = discord.Embed(
                title=f"{ctx.author.display_name} has challenged you to a **{offer}** duel!",
                description="Will you accept? Reply with `duel accept` or `duel deny`",
                color=shade,
            )
            challenge.add_field(
                name=f"{ctx.author.display_name}'s Nebby:",
                value=UserLayer[1],
                inline=True,
            )
            challenge.add_field(name="‎", value="‎", inline=True)
            challenge.add_field(
                name=f"{op.display_name}'s Nebby:",
                value=OpLayer[1],
                inline=True,
            )
            view = offerButtons(
                ctx=ctx,
                op=op,
                offer=offer,
                shade=shade,
                userMon=userMon,
                opMon=opMon,
                UserLayer=UserLayer,
                OpLayer=OpLayer,
            )
            response = await ctx.send(embed=challenge, view=view)
            view.response = response
            await view.wait()


async def setup(bot):
    await bot.add_cog(Dueling(bot))
