from typing import Optional
import discord 
from discord.ext import commands 
import random
import uuid

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import DatabaseInteractor

interactor = DatabaseInteractor()

def get_monster_body(head: str, body: str):
    return f"‎ ‎ {head}\n/{body}\\\n‎ ‎ ‎ |‎ ‎ |"

# Takes in dictionary of monsters with monster info for each, turns into embed for !!monsters
def monster_embed(monstersList: dict, index: int, icon_url: str):
    info = monstersList[index]
    totalPower = info['Attack'] + info['Defense'] + info['Speed'] + info['Intelligence']

    embed = discord.Embed(title=f'"{info["""Name"""]}"', description=f"**Total Power:** {num_suffix(totalPower)}", color=monster_power_color(totalPower))
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="Appearance", value=get_monster_body(info['Head'], info['Body']), inline=False)
    embed.add_field(name="Strength:", value=f"**{num_suffix(info['Attack'])}**", inline=True)
    embed.add_field(name="Defense:", value=f"**{num_suffix(info['Defense'])}**", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)
    embed.add_field(name="Speed:", value=f"**{num_suffix(info['Speed'])}**", inline=True)
    embed.add_field(name="Intelligence:", value=f"**{num_suffix(info['Intelligence'])}**", inline=True)
    embed.add_field(name="‎", value="‎", inline=True)
    embed.set_footer(text=f"Showing monster {index + 1} out of {len(monstersList)}\nid: {info['ID']}")
    return embed

def list_embed(monsters: dict, name: str):
    display = ""
    
    for i, monster in enumerate(monsters):
        totalPower = monster['Attack'] + monster['Defense'] + monster['Speed'] + monster['Intelligence']
        if len(str(i+1)) == 1:
            spaced = f"‎ ‎ {i+1}"
        elif len(str(i+1)) == 2:
            spaced = f"‎ {i+1}"
        else:
            spaced = i+1

        display += f"`{spaced}`‎ ‎ ‎ ‎ {monster['Head']}{monster['Body']} **{monster['Name']}**‎ •‎ {num_suffix(totalPower)} TP\n"

    embed = discord.Embed(title=f"{name}'s monsters", description=display)

    return embed
    

# Tier colors for different ranges of monster power
def monster_power_color(power):
    colors = {
        (0, 1000): discord.Color.light_gray(),
        (1000, 10000): discord.Color.green(),
        (10000, 100000): discord.Color.blue(),
        (100000, 1000000): discord.Color.purple(),
        (1000000, 100000000): discord.Color.orange(),
        (100000000, 1000000000): discord.Color.red(),
        (1000000000, 100000000000): discord.Color.yellow(),
        (100000000000, 1000000000000): discord.Color.pink(),
        (1000000000000, 1000000000000000): discord.Color.from_rgb(255, 255, 255),
        (1000000000000000, 18446744073709551615): discord.Color.from_rgb(0, 0, 0)
    }
    
    for range_, color in colors.items():
        if range_[0] < power < range_[1]:
            return color
    
# Converts large numbers into their appropriate suffixes (k, M, B, etc.)
def num_suffix(num: int):
    suffixes = ['', 'k', 'M', 'B', 'T', 'qd', 'Qn']
    index = 0

    while num >= 1000 and index < len(suffixes) - 1:
        num /= 1000
        index += 1

    return f"{num:.1f}{suffixes[index]}"

# Converts user inputted suffixed numbers into a usable int (ex. 1.2m -> 1200000)
def suffix_num(num):
    suffixes = {
        'k': 3,
        'm': 6,
        'b': 9,
        't': 12,
        'qd': 15,
        'qn': 18,
    }

    num = num.lower()

    # Check if number inputted does not have any suffixes
    try:
        checkNum = float(num)
        return int(checkNum)
    except ValueError:
        pass
    
    # If contains suffixes, convert number accordingly
    for suffix, magnitude in suffixes.items():
        if num.endswith(suffix):
            numPart = num[:-len(suffix)]
            try:
                res = float(numPart)
                return int(res * (10 ** magnitude))
            except ValueError:
                return None
    return None

class navButtons(discord.ui.View):
    def __init__(self, *, timeout=180, monsters, avatar):
        super().__init__(timeout=timeout)
        self.index = 0
        self.monsters = monsters
        self.avatar = avatar

    def indexCheck(self):
        if self.index < 0:
            self.index = 0
        elif self.index >= len(self.monsters):
            self.index = len(self.monsters) - 1

    @discord.ui.button(label="",style=discord.ButtonStyle.blurple, emoji="◀️")
    async def previous(self,interaction:discord.Interaction, button:discord.ui.Button):
        self.index -= 1
        self.indexCheck()
        
        await interaction.response.edit_message(embed=monster_embed(self.monsters, self.index, self.avatar), view=self)

    @discord.ui.button(label="",style=discord.ButtonStyle.blurple, emoji="▶️")
    async def next(self,interaction:discord.Interaction, button:discord.ui.Button):
        self.index += 1
        self.indexCheck()

        await interaction.response.edit_message(embed=monster_embed(self.monsters, self.index, self.avatar), view=self)

class Nebbies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.heads = [":grinning:", ":smiley:", ":smile:", ":grin:", ":laughing:", ":star_struck:", ":sweat_smile:", ":joy:", ":rofl:", ":relieved:", ":blush:", ":innocent:", ":slight_smile:", ":upside_down:", ":wink:", ":relieved:", ":heart_eyes:", ":kissing_heart:", ":kissing:", ":kissing_smiling_eyes:", ":kissing_closed_eyes:", ":yum:", ":zany_face:", ":stuck_out_tongue_winking_eye:", ":stuck_out_tongue_closed_eyes:", ":stuck_out_tongue:", ":money_mouth:", ":hugging:", ":nerd:", ":sunglasses:", ":clown:", ":cowboy:", ":smirk:", ":unamused:", ":disappointed:", ":pensive:", ":worried:", ":confused:", ":slight_frown:", ":frowning2:", ":persevere:", ":confounded:", ":tired_face:", ":weary:", ":triumph:", ":rage:", ":face_with_symbols_over_mouth:", ":woman_gesturing_no:", ":no_mouth:", ":neutral_face:", ":expressionless:", ":hushed:", ":frowning:", ":anguished:", ":open_mouth:", ":dizzy_face:", ":exploding_head:", ":flushed:", ":scream:", ":fearful:", ':baby:', ':child:', ':boy:', ':girl:', ':adult:', ':man:', ':woman:', ':bearded_person:', ':bearded_person:', ':bearded_person:', ':adult:', ':man_red_haired:', ':woman_red_haired:', ':adult:', ':man_curly_haired:', ':woman_curly_haired:', ':adult:', ':man_white_haired:', ':woman_white_haired:', ':adult:', ':man_bald:', ':woman_bald:', ':blond_haired_person:', ':blond_haired_man:', ':blond_haired_woman:', ':older_adult:', ':older_man:', ':older_woman:', ':smiling_imp:', ':imp:', ':skull:', ':skull_crossbones:', ':poop:', ':clown:', ':japanese_ogre:', ':japanese_goblin:', ':ghost:', ':alien:', ':space_invader:', ':robot:', ':smiley_cat:', ':smile_cat:', ':joy_cat:', ':heart_eyes_cat:', ':smirk_cat:', ':kissing_cat:', ':scream_cat:', ':crying_cat_face:', ':pouting_cat:', ':monkey_face:',  ':gorilla:', ':dog:', ':wolf:', ':fox:', ':raccoon:', ':cat:', ':lion_face:', ':tiger:', ':cow:', ':pig:', ':boar:', ':mouse:', ':hamster:', ':rabbit:', ':bear:', ':polar_bear:', ':koala:', ':panda_face:', ':chicken:', ':eagle:', ':egg:', ':frog:', ':new_moon_with_face:', ':full_moon_with_face:', ':sun_with_face:', ':jack_o_lantern:']

        self.bodies = [":koko:", ":sa:", ":u6708:", ":u6709:", ":u6307:", ":ideograph_advantage:", ":u5272:", ":accept:", ":u7981:", ":u5408:", ":u7a7a:", ":u55b6:", ":u6e80:", ":u7121:", ":u6708:", ":u7533:", ":red_circle:", ":orange_circle:", ":yellow_circle:", ":green_circle:", ":blue_circle:", ":purple_circle:", ":brown_circle:", ":black_circle", ':soccer:', ':baseball:', ':softball:', ':basketball:', ':volleyball:', ':heart:', ':orange_heart:', ':yellow_heart:', ':green_heart:', ':blue_heart:', ':purple_heart:', ':brown_heart:', ':black_heart:', ':white_heart:', ':heart_on_fire:', ':mending_heart:', ':new_moon:', ':first_quarter_moon:', ':waxing_gibbous_moon:', ':waning_gibbous_moon:', ':last_quarter_moon:', ':lab_coat:', ':safety_vest:', ':necktie:', ':shirt:', ':dress:', ':one_piece_swimsuit:', ':bikini:', ':womans_clothes:', ':musical_keyboard:', ':atom:', ':infinity:', ':peace:', ':name_badge:', ':o:', ':eight_spoked_asterisk:', ':radioactive:', ':biohazard:', ':8ball:', ':cookie:', ':rice_cracker:', ':rice_ball:', ':apple:', ':green_apple:', ':radio_button:', ':white_square_button:', ':peach:', ':tomato:', ':star2:', ':chestnut:', ':gem:', ':red_square:', ':orange_square:', ':yellow_square:', ':green_square:', ':blue_square:', ':purple_square:', ':brown_square:']

        
    # Process to create a monster
    @commands.command(pass_context=True)
    async def create(self, ctx):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("You have not registered. Please register with !!setup.")
        else:
            embed = discord.Embed(color=discord.Color.purple(), title="Build-a-Nebby", description="How much tokens will you sacrifice?")
            await ctx.send(embed=embed)

            def check(m):
                checkNum = suffix_num(m.content)
                return checkNum != None and m.channel == ctx.channel and checkNum > 10 and checkNum <= interactor.get_user_balance(ctx.author.id) and m.author == ctx.author
            msg = await self.bot.wait_for('message', check=check)

            # Calculating monster's stats and adding to DB
            totalStatDist = suffix_num(msg.content) / 4
            DIST_LOW = 0.75
            DIST_HIGH = 1.25

            stats = ['atk', 'spd', 'intl', 'defe']
            values = {}

            for stat in stats:
                values[stat] = random.randint(int(totalStatDist * DIST_LOW), int(totalStatDist * DIST_HIGH))

            atk = values['atk']
            spd = values['spd']
            intl = values['intl']
            defe = values['defe']

            await ctx.send(embed=discord.Embed(color=discord.Color.purple(), title=f"You placed {num_suffix(suffix_num(msg.content))} Tokens in the pot.", description="What will you name your monster? (50 character limit)"))

            def name_check(m):
                return len(m.content) <= 50 and m.author == ctx.author and m.channel == ctx.channel
            name = await self.bot.wait_for('message', check=name_check)
            
            randHead = random.choice(self.heads)
            randBody = random.choice(self.bodies)
            randId = str(uuid.uuid4())
            
            interactor.create_monster(randId, ctx.author.id, name.content, atk, defe, spd, intl, randHead, randBody)
            interactor.subtract_tokens(ctx.author.id, suffix_num(msg.content))
            if interactor.get_selected_monster(ctx.author.id) == "None":
                interactor.set_selected_monster(ctx.author.id, randId)

            # Display newly created monster to user
            embed=discord.Embed(color=monster_power_color(suffix_num(msg.content)), title=name.content, description=f"**Tokens Sacrificed:** {msg.content}\n**Total Power: {num_suffix(atk+defe+spd+intl)}**")
            embed.set_author(name=f"{ctx.author.name}'s Monster", icon_url=ctx.author.avatar.url)
            embed.add_field(name="Appearance:", value=get_monster_body(randHead, randBody), inline=False)
            embed.add_field(name="Strength:", value=f"**{num_suffix(atk)}**", inline=True)
            embed.add_field(name="Defense:", value=f"**{num_suffix(defe)}**", inline=True)
            embed.add_field(name="‎", value="‎", inline=True)
            embed.add_field(name="Speed:", value=f"**{num_suffix(spd)}**", inline=True)
            embed.add_field(name="Intelligence:", value=f"**{num_suffix(intl)}**", inline=True)
            embed.add_field(name="‎", value="‎", inline=True)
            embed.set_footer(text=f"id: {randId}")
            await ctx.send("Monster successfully created.", embed=embed)
    
    # Display all users' monsters (in full detail or simplified list)
    @commands.command(pass_context=True)
    async def monsters(self, ctx, view):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("You have not registered. Please register with !!setup.")
        elif view == None or view not in ("list", "info"):
            await ctx.send("Incorrect command usage. Correct command usage: !!monsters `list/info`")
        elif view == "info":
            monsters = interactor.get_monsters(ctx.author.id)
            await ctx.send(embed=monster_embed(monsters, 0, ctx.author.avatar.url), view=navButtons(monsters=monsters, avatar=ctx.author.avatar.url))
        else:
            monsters = interactor.get_monsters(ctx.author.id)
            await ctx.send(embed=list_embed(monsters, ctx.author.name))
    
    # Select a monster to put into fight by name
    @commands.command(pass_context=True)
    async def select(self, ctx, *, name):
        if not interactor.does_user_exist(ctx.author.id):
            await ctx.send("You have not registered. Please register with !!setup.")
        else:
            found = []
            monsters = interactor.get_monsters(ctx.author.id)
            
            # Get all monsters with the same name (including identical ones)
            for monster in monsters:
                if monster['Name'] == name:
                    found.append(monster)
            if not found:
                await ctx.send(f'No monsters found with the name "{name}".')
            elif len(found) == 1:
                interactor.set_selected_monster(ctx.author.id, found[0]['ID'])
                await ctx.send(f"Monster ({name}) has been selected.")
            else: # If multiple monsters are found, prompt user to select which one to select out of the duplicate monster names
                foundList = "Select a monster with `select (number)`\n\n"
                for i, stat in enumerate(found):
                    totalPower = stat['Attack'] + stat['Defense'] + stat['Speed'] + stat['Intelligence']
                    if len(str(i+1)) == 1:
                        spaced = f"‎ ‎ {i+1}"
                    elif len(str(i+1)) == 2:
                        spaced = f"‎ {i+1}"
                    else:
                        spaced = i+1

                    foundList += f"`{spaced}`‎ ‎ ‎ ‎ {stat['Head']}{stat['Body']} **{stat['Name']}**‎ •‎ {num_suffix(totalPower)} TP\n"
                
                embed = discord.Embed(title=f"{len(found)} identical monsters found.", description=foundList)
                await ctx.send(embed=embed)

                def responseCheck(m):
                    return m.content.startswith("select ") and m.author == ctx.author and m.channel == ctx.channel and m.content[7:].isdigit() and int(m.content[7:]) > 0 and int(m.content[7:]) <= len(foundList)
                selection = await self.bot.wait_for('message', check=responseCheck)
                
                interactor.set_selected_monster(ctx.author.id, found[int(selection.content[7:]) - 1]['ID'])
                await ctx.send(f"Monster ({name}) has been selected.")

                
                




async def setup(bot):
    await bot.add_cog(Nebbies(bot))