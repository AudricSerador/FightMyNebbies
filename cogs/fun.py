from discord.enums import ButtonStyle
from discord.ext import commands
import discord
import random
import time

def getFormattedTime(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{mins:02d}:{secs:02d}.{ms:03d}"

class TimerButton(discord.ui.View):
    def __init__(self, *, timeout: 86400, user, start):
        super().__init__(timeout=timeout)
        self.user = user
        self.start = start
        self.laps = []
    
    async def stopwatchEmbed(self, interaction):
        seconds = abs(self.start - time.time())
        lapsText = ""
        for i, lap in enumerate(self.laps):
            if len(str(i+1)) == 1:
                spaced = f"‎ ‎ {i+1}"
            elif len(str(i+1)) == 2:
                spaced = f"‎ {i+1}"
            else:
                spaced = i+1
                
            lapsText += f"`{spaced}`‎ ‎ ‎ ‎ {getFormattedTime(lap)}\n"
        
        embed = discord.Embed(title=f"⏱️ Stopwatch",
                            description=f"# {getFormattedTime(seconds)}")
        embed.add_field(name="Laps", value=lapsText)
        await interaction.edit_original_response(embed=embed)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message(
                f"Only {self.user.display_name} can stop the stopwatch.",
                ephemeral=True,
            )
            return False
        return True
    
    @discord.ui.button(label="Lap")
    async def lap_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        lapSeconds = abs(self.start - time.time())
        self.laps.append(lapSeconds)
        
        await interaction.response.defer()
        await self.stopwatchEmbed(interaction)
    
    @discord.ui.button(label="Stop", style=ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        self.laps = []
        for button in self.children:
            button.disabled = True
        await interaction.response.defer()
        await self.stopwatchEmbed(interaction)

        

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.phrases = ["kys (keep yourself safe)", ":nerd:", "who asked"]
        self.eightball = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes - definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely," "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "Outlook not so good",
            "Very doubtful",
            "HELLLL NAH",
            "Yes on god no cap fr fr",
            "stfu",
        ]

    # Bruh
    @commands.command()
    async def bruh(self, ctx):
        await ctx.send(random.choice(self.phrases))

    # 1984
    @commands.command(name="1984")
    async def literally(self, ctx, opponent: discord.Member = None):
        await ctx.send(f"literally 1984.")

    # 8 ball
    @commands.command(name="8ball")
    async def _8ball(self, ctx):
        embed = discord.Embed(
            color=discord.Color.purple(),
            title=":8ball: 8ball says...",
            description=f"{random.choice(self.eightball)}",
        )
        await ctx.send(embed=embed)
    
    # Stopwatch
    @commands.command(name="stopwatch")
    async def stopwatch(self, ctx):
        t1 = time.time()
        seconds = abs(t1 - time.time())
        embed = discord.Embed(title=f"⏱️ Stopwatch",
                            description=f"# {getFormattedTime(seconds)}")
        embed.add_field(name="Laps", value="None")
        await ctx.send(embed=embed, view=TimerButton(start=t1, user=ctx.author, timeout=180))
        


async def setup(bot):
    await bot.add_cog(Fun(bot))
