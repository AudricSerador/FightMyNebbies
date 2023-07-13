import discord
from discord.ext import commands
from discord import Button, ButtonStyle
import random
import asyncio
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
        return discord.Embed(color=discord.Color.green(), title=":white_check_mark: CORRECT!!!!", description=f"You have won {num_suffix(reward)} Tokens.")
    else:
        return discord.Embed(color=discord.Color.red(), title=":x: WRONG!!!!", description="You're actually retarded")

def getRandomAnswer():
    answers = ["infinite games but no bacon", "no games, no bacon", "infinite games, no games, but some games, and some bacon on the side", "games, games, oh so many games, but no bacon", "infinite games but also an uncountably infinite amount of games", "no bacon but some games", "some games but also some more games with some bacon", "unlimited games but only with bacon", "no games but with some games and infinite bacon", "only just one game to your lineage", "negative bacon", "negative games", "infinite negative bacon with infinite games", "3 bacon", "17 games", "baconless games forever", "gameless bacon feast", "games galore, but bacon no more", "a bacon-free game extravaganza", "endless games, but bacon's amiss", "a touch of games, sans bacon", "unlimited bacon, limited games", "games without bacon, a peculiar twist", "baconless entertainment, boundless games", "the great game-bacon paradox", "games aplenty, yet bacon is scarce", "no games, all bacon, a unique trade", "game overload, baconless delight", "a bacon-driven game marathon", "games abound, bacon eludes", "bacon famine, game feast", "a never-ending game buffet without bacon", "baconless challenges, game-filled days", "the eternal quest for games and bacon", "bacon's absence, games' abundance", "a baconless gameverse", "endless bacon chase, limited games", "the enigma of games and the missing bacon", "games without borders, baconless horizons", "bacon's vanishing act, games persist", "a world of games, a shortage of bacon", "bacon withdrawal, game immersion", "games multiply, bacon diminishes", "the bacon paradox in a world of games", "games galore, bacon no more", "bacon deprivation, game addiction", "games unlimited, bacon on the wane", "a game-filled universe, devoid of bacon", "the grand game-bacon experiment", "baconless battles, game conquests", "games transcend, bacon recedes", "bacon scarcity, game abundance", "a game trove, a baconless reality", "the allure of games, the absence of bacon", "baconless adventures in a realm of games", "games unbounded, bacon forgotten", "the vanishing bacon conundrum", "the infinite game spectrum, bacon excluded", "bacon eludes, games endure", "games flourish, bacon dwindles", "bacon shortage, game abundance", "a realm bereft of bacon, teeming with games", "the game-bacon duality, in perpetual balance", "bacon's absence, games' ubiquity", "games without bacon, a realm extraordinary", "bacon's scarcity, games' abundance persists", "a world of games, a dearth of bacon", "baconless quests, game-filled odysseys", "games multiply, bacon diminishes endlessly", "the bacon enigma, the allure of games", "game haven, baconless paradise", "bacon's scarcity, games' overflow", "a game-filled universe, devoid of bacon's taste", "the grand experiment of game and bacon", "baconless battles, game conquests without end", "games unbounded, bacon forgotten", "the elusive bacon, the enduring game", "bacon scarcity, game abundance without respite", "a realm bereft of bacon, teeming with ceaseless games", "the game-bacon duality, in perpetual equilibrium", "bacon eludes, games endure relentlessly", "games flourish, bacon dwindles persistently", "bacon shortage, game abundance prevails", "a realm without bacon, a world of games forever", "baconless quests, game-filled odysseys unending", "games multiply, bacon diminishes endlessly", "the bacon enigma, the labyrinth of games unending", "game haven, baconless paradise eternal", "bacon-starved game enthusiasts unite forever", "games overflow, bacon retreats eternally", "bacon's scarcity, games' infinity without end", "a game wonderland, bacon forgotten forever", "the elusive bacon, the everlasting game unceasing", "baconless realms, game-filled realms forever", "games in plenty, bacon in want perpetually", "bacon's scarcity, games' expanse without bounds", "the game's bounty, the bacon's lament eternal", "games infinite, bacon finite indefinitely", "bacon's scarcity, game abundance prevails perpetually", "a world of games, a world without bacon forever", "baconless challenges, game-filled"]
    return random.choice(answers)
                

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180, userID):
        self.userID = userID
        self.one.label = getRandomAnswer()
        self.two.label = getRandomAnswer()
        self.three.label = getRandomAnswer()
        self.four.label = getRandomAnswer()
        super().__init__(timeout=timeout)   
        
    @discord.ui.button(style=discord.ButtonStyle.success)
    async def one(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(embed=questionRNG(self.userID), view=self)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def two(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(embed=questionRNG(self.userID), view=self)

    @discord.ui.button(style=discord.ButtonStyle.success)
    async def three(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(embed=questionRNG(self.userID), view=self)
    
    @discord.ui.button(style=discord.ButtonStyle.success)
    async def four(self,interaction:discord.Interaction,button:discord.ui.Button):
        for child in self.children:
            child.disabled=True
        await interaction.response.edit_message(embed=questionRNG(self.userID), view=self)

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bigquestion", pass_context=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def BigQuestion(self, ctx):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("User is not registered. Please register with !!setup.")
        else:
            embed = discord.Embed(color=discord.Color.dark_purple(), title="Iron's Big Question", description="Would you rather have...")
            await ctx.send(embed=embed, view=Buttons(userID=ctx.author.id))
            

async def setup(bot):
    await bot.add_cog(Minigames(bot))