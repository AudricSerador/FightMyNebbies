import json
import os
import random

import discord
from discord.ext import commands

os.chdir(r"C:\Users\their\PycharmProjects\pythonProject")

client = commands.Bot(command_prefix="g!")

mainshop = [{"name": "Watch", "price": 100, "description": "Time"},
            {"name": "Laptop", "price": 100, "description": "Work"},
            {"name": "PC", "price": 100, "description": "Gaming <:sadgamer:706658222144094230>"}, ]


@client.event
async def on_ready():
    print("Bot is Starting")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Bruh Stop Spamming Random Shit and Do an Actual Command.")

    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send("Bruh Stop Spamming and Actually wait to do the Command again in {:.2f}s".format(error.retry_after))


@client.command(aliases=["bal", 'Bal'])
@commands.cooldown(1, 3, commands.BucketType.user)
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["Wallet"]
    bank_amt = users[str(user.id)]["Bank"]

    em = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.blue())
    em.add_field(name="Bobux in Wallet", value=wallet_amt)
    em.add_field(name="Bobux in Bank", value=bank_amt)
    await ctx.send(embed=em)


@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(101)

    await ctx.send(f"Someone gave you {earnings} coins good job retard")

    users[str(user.id)]["Wallet"] += earnings

    with open("Money.json", "w") as f:
        json.dump(users, f, indent=4)


@client.command(aliases=["With", "with"])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount is None:
        await ctx.send("Please enter the amount Dumbass")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You don't have that much money Retard")
        return
    if amount < 0:
        await ctx.sned("Amount must be positive Dumbass")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, "Bank")

    await ctx.send(f"You withdrew {amount} Bobux")


@client.command(aliases=['dep', 'Dep'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount is None:
        await ctx.send("Please enter the amount Dumbass")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("You don't have that much money Retard")
        return
    if amount < 0:
        await ctx.sned("Amount must be positive Dumbass")
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, "Bank")

    await ctx.send(f"You deposited {amount} Bobux")


@client.command(aliases=['withall', 'WithAll'])
async def withdrawall(ctx):
    await open_account(ctx.author)

    bal = await update_bank(ctx.author)
    amount = int(bal[1])

    if amount == 0:
        await ctx.send("There is nothing to Withdraw from the Bank Retard")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, "Bank")

    await ctx.send(f"You withdrew {amount} Bobux")


@client.command(aliases=['depall', 'DepAll'])
async def depositall(ctx):
    await open_account(ctx.author)

    bal = await update_bank(ctx.author)
    amount = int(bal[0])

    if amount == 0:
        await ctx.send("There is nothing to Deposit Into the Bank Dumbass")
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, "Bank")

    await ctx.send(f"You deposited {amount} Bobux")


@client.command(aliases=['Send'])
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)

    if amount is None:
        await ctx.send("Please enter the amount Dumbass")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You don't have that much money Retard")
        return
    if amount < 0:
        await ctx.sned("Amount must be positive Dumbass")
        return

    await update_bank(ctx.author, -1 * amount, "Bank")
    await update_bank(member, amount, "Bank")

    await ctx.send(f"You Gave {member.display_name} {amount} Bobux")


@client.command(aliases=['Rob'])
@commands.cooldown(1, 300, commands.BucketType.user)
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0] < 100:
        await ctx.send(f"Bruh it aint worth Robbing {member.display_name} because they are fucking poor (<100 Bobux)")
        return

    earnings = random.randrange(0, bal[0])
    fail = random.randint(1, 2)
    if fail == 1:
        await update_bank(ctx.author, earnings)
        await update_bank(member, -1 * earnings)
        await ctx.send(f"You Robbed {member.display_name} and successfully stole {earnings} Bobux.")
    else:
        await ctx.send(f"Good job Dumbass {member.display_name} kept their door locked causing you to get no Bobux.")


@client.command(aliases=['Gomble'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def gomble(ctx, amount=None):
    await open_account(ctx.author)

    if amount is None:
        await ctx.send("Please enter the amount Dumbass")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("You don't have that much money Retard")
        return
    if amount < 0:
        await ctx.sned("Amount must be positive Dumbass")
        return

    final = []
    for i in range(3):
        a = random.choice(["<:sadgamer:706658222144094230>", "<:weirdchamp2:706603593192439830>",
                           "<:babyrage2:705116097484947536>", "<:pog2:714227973418385489>",
                           "<:nerdpog:704942403676667984>"])

        final.append(a)

    if final[0] == final[1] or final[1] == final[2] or final[2] == final[0]:
        await update_bank(ctx.author, 2 * amount)
        await ctx.send(f"{str(final)}\nGGEZ You Won The Bet! (There's a Match 2x Bobux)")
    else:
        await update_bank(ctx.author, -1 * amount)
        await ctx.send(f"{str(final)}\nGomble Gomble MotherFucker! (No Matches Bobux is Gone)")


@client.command(aliases=["Shop", "Store"])
async def shop(ctx):
    em = discord.Embed(title="Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name=name, value=f"[{price} Bobux | {desc}]")

    await ctx.send(embed=em)


@client.command()
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there Dumbass.")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return


    await ctx.send(f"GGEZ You just bought {amount} {item}")


@client.command(aliases=["Bag", "Inventory", "inventory"])
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["Bag"]
    except:
        bag = []


    em = discord.Embed(title = "Bag")
    for item in bag:
        name = item["Item"]
        amount = item["Amount"]

        em.add_field(name = name, value = amount)

    await ctx.send(embed = em)


async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Bag"]:
            n = thing["Item"]
            if n == item_name:
                old_amt = thing["Amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["Bag"][index]["Amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            obj = {"Item":item_name , "Amount" : amount}
            users[str(user.id)]["Bag"].append(obj)
    except:
        obj = {"Item":item_name , "Amount" : amount}
        users[str(user.id)]["Bag"] = [obj]

    with open("Money.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"Wallet")

    return [True,"Worked"]


@client.command(aliases = ["Sell"])
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there Dumbass!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have {amount} {item} in your bag Retard.")
            return
        if res[1]==3:
            await ctx.send(f"You don't have {item} in your bag Retard.")
            return

    await ctx.send(f"You just sold {amount} {item}.")

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.9* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Bag"]:
            n = thing["Item"]
            if n == item_name:
                old_amt = thing["Amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["Bag"][index]["Amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            return [False,3]
    except:
        return [False,3]

    with open("Money.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"Wallet")

    return [True,"Worked"]


@client.command(aliases = ["lb"])
async def leaderboard(ctx,x = 5):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["Wallet"] + users[user]["Bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)

    em = discord.Embed(title = f"Top {x} Richest People" , description = "Da 1%",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        em.add_field(name = f"{index}. IDK You Figure It Out" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)

async def open_account(user):
    with open("Money.json", "r") as f:
        users = json.load(f)

        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["Wallet"] = 0
            users[str(user.id)]["Bank"] = 0

        with open("Money.json", "w") as f:
            json.dump(users, f, indent=4)


async def get_bank_data():
    with open('Money.json', 'r') as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode="Wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("Money.json", "w") as f:
        json.dump(users, f, indent=4)

    bal = [users[str(user.id)]["Wallet"], users[str(user.id)]["Bank"]]
    return bal


client.run("")