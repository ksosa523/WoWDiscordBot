import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import requests
import json
from bs4 import BeautifulSoup

load_dotenv()
client = commands.Bot(command_prefix="!")
client.remove_command("help")
#API_CLIENT_ID = "313494b9835645e38035c3c869ed554a"
#API_CLIENT_SECRET = "E8wb0Q0Hh0MwQ2P1LDDHsuFVzliDMQZg"
WOW_REGION = "us"
#DISCORD_TOKEN = 'NzcwNDg5MzcyMzk4NDUyNzc2.X5eUJQ.bMwPwJjzQDfmkT5K_3XJCyT4FN8'

API_CLIENT_ID = os.getenv("API_CLIENT_ID")
API_CLIENT_SECRET = os.getenv("API_CLIENT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# get token
r = requests.post("https://us.battle.net/oauth/token", data={"grant_type": "client_credentials"},
                  auth=(API_CLIENT_ID, API_CLIENT_SECRET))
res = json.loads(r.text)
access_token = res["access_token"]
print(r.text)

#TO DO
#make lowercase and remove '"-` from all args
#list of quotes to randomize for description
#FIX DECRIPTION QUOTE
#what else do y'all WANT
#web scrape wowHead for items + quests

#UI
#change color for horde or alliance


@client.event
async def on_message(message):  # listen to all messages
    if message.author == client.user:  # ignore my own messages
        return
    await client.process_commands(message)
    if message.content.startswith('!stats'):
        stat = message.content.split(" ", 2)
        print(stat)


@client.command()
async def stats(ctx, arg1, arg2):
    arg1 = arg1.lower()
    arg2 = arg2.replace(" ","").replace("'","").replace("-","").lower()
    prof = requests.get("https://us.api.blizzard.com/profile/wow/character/" + arg2 + "/" + arg1,
                        params={"namespace": "profile-us", "locale": "en_US", "access_token": access_token})
    print(prof.url) #testing url
    print(arg1)
    print(arg2)
    if prof.status_code == 200:
        data = json.loads(prof.text)
        img = get_thumbnail(arg2, arg1)
        embed = display_stat(data, img)
        await ctx.send(content=None, embed=embed)

    else:
        print(prof.status_code)
        await ctx.send("I couldn't find that, try typing it correctly this time scrub")

@client.command()
async def todaywow(ctx):
    page = requests.get("https://www.wowhead.com/")
    soup = BeautifulSoup(page.content, "html.parser")
    bfa_world_boss = soup.find_all(id="US-group-epiceliteworldbfa")
    results=[];
    url ="https://www.wowhead.com"
    for b in bfa_world_boss :
        names = b.find_all(class_="tiw-line-name")
        #print(names.find("a"))
        #print(names.text)
        for n in names:
            link = str(n.a["href"])
            info = {
                "name": n.text,
                "link": url+link
            }
            results.append(info)
            #print(n.a["href"])
            #print(results[0]["link"])

    em1 = discord.Embed(
        title="Today in WoW",
        type="rich",
        description="Just some stuff you should know, just in case",
        colour=discord.Colour.dark_teal()
    )
    #'\u200b' <- zero with space
    em1.add_field(name='BFA WORLD BOSS', value="https://www.wowhead.com/world-quests/bfa/na", inline=False)
    for i, n in enumerate(results):
        em1.add_field(name=results[i]["name"], value=results[i]["link"], inline=False)


    await ctx.send(content=None, embed=em1)
    #await ctx.send("look at log")

@client.command()
async def help(ctx):
    em2 = discord.Embed(
        title="Possible Commands",
        color=discord.Colour.purple()
    )

    em2.add_field(name="!stats", value="Provides player information such as: Faction, Race, Class, Level, Average Item level", inline=False)
    em2.add_field(name="!todaywow",value="Provides BFA World Boss information from WoWHead", inline=False)
    em2.add_field(name="!todaywow", value="Provides BFA World Boss information from WoWHead", inline=False)
    await ctx.send(content=None, embed=em2)

def get_thumbnail(realm,character_name):
    r = requests.get("https://us.api.blizzard.com/profile/wow/character/"+realm +"/"+character_name+"/character-media",
                     params={"namespace": "profile-us", "locale": "en_US", "access_token": access_token})
    media = json.loads(r.text)
    img = media["assets"][0]["value"]
    #different possible views
    # message.set_thumbnail(url="https://render-us.worldofwarcraft.com/character/malganis/128/118688128-inset.jpg")
    # message.set_image(url="https://render-us.worldofwarcraft.com/character/malganis/128/118688128-main-raw.png")
    return img

def display_stat(data, img):
    # Name, Race, Class, Level, Average Item Level
    em = discord.Embed(
        title=data["name"],
        type="rich",
        description="What we do now, we do for the Horde, both of us.",
        colour=discord.Colour.red()
    )
    em.set_thumbnail(url=img)
    em.add_field(name="Faction", value=data["faction"]["name"], inline=True)
    em.add_field(name="Race", value =data["race"]["name"], inline=True)
    em.add_field(name="Class", value=data["character_class"]["name"], inline=True)
    em.add_field(name="Level", value=data["level"], inline=True)
    em.add_field(name="Average Item Level", value=data["average_item_level"], inline=True)
    em.set_footer(text="       ")

    return em


client.run(DISCORD_TOKEN)
