import asyncio
import discord
import os
import json
from discord.ext.commands import Bot
from checks import is_year
from discord.ext import commands

from mongodb_connector import MongoDBConnector

roles = []
guild = None
desc = 'A bot made by server admins to manage KeyGEnCoders discussion Server'
loop = asyncio.get_event_loop()
bot = Bot(command_prefix=commands.when_mentioned_or("!"), description=desc, loop=loop)
db_connector = MongoDBConnector(os.getenv('MONGODB_SRV'), db_name='discord_db', loop=loop)

with open("colour.json") as file:
    colours_hex = json.load(file)
    colours = [discord.Colour(int(colour, 16)) for colour in colours_hex]


def get_year(member):
    for role in member.roles:
        if is_year(role.name):
            return role.name


@bot.event
async def on_ready():
    global roles
    global guild

    guild = bot.guilds
    guild = guild[0]
    roles = guild.roles
    game = discord.Game(name="Judgement Day")
    await bot.change_presence(status=discord.Status.idle, activity=game)
    members = bot.get_all_members()
    for member in members:
        if member.top_role.is_default():
            if member.dm_channel is None:
                await member.create_dm()
            dmchannel = member.dm_channel
            await dmchannel.send("Hey Warrior, It seems no roles is assigned to you, Type !setyear 'Your passout year' to get your role! :) ")


@bot.command(hidden=True)
async def setyear(ctx, arg):
    """
    Sets your passout year as a role
    """
    global guild
    global roles
    role = None
    member = guild.get_member(ctx.message.author.id)

    if is_year(arg):
        for role_ in roles:
            if role_.name == arg:
                role = role_
                break

        year_added = any(is_year(role.name) for role in member.roles)
        if role is not None:

            if year_added:
                await ctx.send("You already have a year assigned to you! If you want to change it contact an admin :)")
            else:
                await member.add_roles(role)
                await ctx.send("Year added!")
        else:
            await ctx.send("Oops there are no such roles now, Please contact any admin for assistance")

    else:
        await ctx.send("The correct format is !setyear YYYY ")


@bot.command()
async def memberstats(ctx):
    """ Shows member stats of the guild """
    global roles
    msg = "Total : " + str(guild.member_count)
    for i in range(1,len(roles)):
        msg = msg+"\n{0.name} : {1}".format(roles[i], len(roles[i].members))
    await ctx.send(msg)


@bot.command(hidden=True)
async def setcurr(ctx,arg):
    """
    Yearly update of colour (Only for admins)
    """
    global colours
    if is_year(arg):
        arg = int(arg)
    else:
        await ctx.send("The correct format is !setcurr YYYY ")
        return

    member = guild.get_member(ctx.message.author.id)
    if member.top_role.name != "admin":
        await ctx.send("You don't have permissions to use this command")
    else:
        for role in roles:
            if is_year(role.name):
                if int(role.name) < arg:
                    await role.edit(colour=colours[4])
                else:
                    await role.edit(colour=colours[3+arg-int(role.name)])
        await ctx.send("Role colours updated!")


@bot.event
async def on_member_join(member):
    if member.dm_channel is None:
        await member.create_dm()
    dmchannel = member.dm_channel
    await dmchannel.send("Welcome to KeyGEnCoders Server!, Type !setyear 'Your passout year' to get started :)")


bot.run(os.getenv('TOKEN'))
