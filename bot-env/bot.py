import discord
import os
import time
from dotenv import load_dotenv
from discord.ext import commands
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
load_dotenv()
client = commands.Bot(command_prefix="!")
client.remove_command("help")
WOW_REGION = "us"
guild_browsers = {}
API_CLIENT_ID = os.getenv("API_CLIENT_ID")
API_CLIENT_SECRET = os.getenv("API_CLIENT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# get token
r = requests.post("https://us.battle.net/oauth/token", data={"grant_type": "client_credentials"},
                  auth=(API_CLIENT_ID, API_CLIENT_SECRET))
res = json.loads(r.text)
access_token = res["access_token"]
print(r.text)
#Icons made by Those Icons : https://www.flaticon.com/authors/those-icons"

#daily text pa que no pongamos dique espiritual
@client.command()
async def dailytext(ctx):
    #page to scrape
    home_page = requests.get("https://wol.jw.org/en/wol/h/r1/lp-e")
    soup = BeautifulSoup(home_page.content, "html.parser") #chicken noodle soup
    #starting div containers
    day = soup.find(id="p5").string
    bibleText = soup.find(id="p6").string
    comment = soup.find(id="p7").string
    
    em = discord.Embed(
      title=day,
      type="rich",
      description="https://wol.jw.org/en/wol/h/r1/lp-e",
      colour=discord.Colour.dark_magenta()
    )
    
    em.add_field(name='bibleText', value='comment', inline=False)
    await ctx.send(content=None, embed=em)
    

@client.command()
async def stats(ctx, arg1, *,arg2):
    arg1 = arg1.lower()
    print(arg2)
    arg2 = arg2.replace(" ","-").replace("'","").replace("’","").replace("`","").lower()
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
    #pages to scrape
    home_page = requests.get("https://www.wowhead.com/")
    world_quests = requests.get("https://www.wowhead.com/world-quests/bfa/na")
    soup = BeautifulSoup(home_page.content, "html.parser")
    soup1 = BeautifulSoup(world_quests.content, "html.parser")
    #starting div containers
    bfa_world_boss = soup.find_all(id="US-group-epiceliteworldbfa")
    bfa_quests = soup1.find_all(id="world-quests-header")
    world_boss=[]
    emmissary_quests=[]
    url ="https://www.wowhead.com"
    for e in bfa_quests:
        quests = e.find_all("dt")
        for q in quests:
            link = str(q.a["href"])
            info = {
                "name": q.text,
                "link": url + link
            }
            emmissary_quests.append(info)
            #print(q.text)
            print(emmissary_quests)

    for b in bfa_world_boss :
        names = b.find_all(class_="tiw-line-name")
        for n in names:
            link = str(n.a["href"])
            info = {
                "name": n.text,
                "link": url+link
            }
            world_boss.append(info)

    em1 = discord.Embed(
        title="Today in WoW",
        type="rich",
        description="https://www.wowhead.com/world-quests/bfa/na",
        colour=discord.Colour.dark_magenta()
    )
    #'\u200b' <- zero with space
    em1.add_field(name='BFA World Boss', value="\u200b", inline=False)
    for i, n in enumerate(world_boss):
        em1.add_field(name=world_boss[i]["name"], value=world_boss[i]["link"], inline=False)
    em1.add_field(name='\u200b', value="\u200b", inline=False)
    em1.add_field(name='Emissary Quests', value="\u200b", inline=False)
    for i, n in enumerate(emmissary_quests):
        em1.add_field(name=emmissary_quests[i]["name"], value=emmissary_quests[i]["link"], inline=True)

    await ctx.send(content=None, embed=em1)
    #await ctx.send("look at log")

@client.command()
async def search(ctx, *, args, search_info=None):
    # added this here to make search faster
    start = time.clock()
    await ctx.send("Please wait while I search")
    print("start")

    if ctx.guild.id in guild_browsers:
    #search WoWHead
        browser = guild_browsers[ctx.guild.id]
        print(guild_browsers[ctx.guild.id])
        await ctx.send("Searching, don't worry...yet")
    else:
        browser = webdriver.Chrome()
        browser.get("https://www.wowhead.com/")
        guild_browsers[ctx.guild.id] = browser
        await ctx.send("I'm still trying")

    print("moving on")
    search_bar = browser.find_element_by_xpath("/html/body/div[5]/div/div[2]/div[1]/form/input")
    search_bar.clear()
    search_bar.send_keys(args)
    search_bar.send_keys(Keys.RETURN)
    url = browser.current_url
    #print(url)
    search_info = []
    result_page = requests.get(url)
    soup = BeautifulSoup(result_page.content, "html.parser")
    print("found page, getting result")
    search_top = soup.find_all(class_="search-results-top")
    print("search_type = 0")
    search_type = 0
    url = "https://www.wowhead.com"
    if not search_top:
        search_type = 1
        print("search_type = 1")
        search_highlight = soup.find_all(class_="search-highlight-results")
        if not search_highlight:
            search_type = 2
            search_exact = soup.find_all(class_="guide-image-links guide-image-links-rows")
        if not search_exact:
            search_type = 3
            print("search_type = 3")

    print("do we get here?")
    if search_type == 0:
        print("search_type top 0")
        time.sleep(0.7)
        result_page = browser.page_source
        soup1 = BeautifulSoup(result_page, "html.parser")
        top_results = soup1.find_all(class_="top-results-result-link")
        print(top_results)
        for t in top_results:
            print(url+t["href"])
            print(t.text)
            info = {
                "name": t.text,
                "link": url+t["href"]
            }
            search_info.append(info)
        for s in search_top:
            time.sleep(0.7)
            ##tr = top_results.get_attribute("href")
            # print(tr)
            # print(tr.text)
            # print(top_results)
            guides = s.find_all(class_="guide-image-link-text-title")
            guide_links = s.find_all("a", href=True)
            x = []  # to hold links
            y = []  # to hold guide titles
            # for tr in top_results:
            #     print(tr)
            #     print(tr["href"])
            #     print(tr.text)
            for link in guide_links:
                x.append(link["href"])
            print("still in 1")
            for titles in guides:
                y.append(titles.text)
            info = {
                "name": "Top Guides",
                "link": '\u200b'
            }
            search_info.append(info)
            for i, j in zip(y, x):
                #print(i)
                #print(j)
                info = {
                    "name": i,
                    "link": url + j
                }
                search_info.append(info)
        print(search_info)
        em = display_search(search_info, 0)
        print("display 0")
        await ctx.send(content=None, embed=em)
    elif search_type == 1:
        print("search_type highlight 1")
        for h in search_highlight:
            link = h.find_all("a", href=True)
            titles = h.find_all(class_="graphical-button-title")
            # print(titles)
            for l in link:
                print(l["href"])
                llink = l["href"]
                if url not in l["href"]:
                    llink = url + l["href"]
            for t in titles:
                print(t.text)
                info = {
                    "name": t.text,
                    "link": llink
                }
                search_info.append(info)
        print(search_info)
        em = display_search(search_info, 1)
        await ctx.send(content=None, embed=em)
    elif search_type == 2:
        print("search_type exact 2")
        for s in search_exact:
            link = s.find_all("a", href=True)
        for l in link:
            print(l["href"])
            print(l.text)
            info = {
                "name": l.text,
                "link": l["href"]
            }
            search_info.append(info)
        extra_url = browser.current_url
        info = {
            "name": "Main Link: ",
            "link": extra_url
        }
        search_info.append(info)
        em = display_search(search_info, 2)
        await ctx.send(content=None, embed=em)
    elif search_type == 3:
        print("search_type google results 3")
        time.sleep(0.7)
        google_result = browser.find_element_by_css_selector(
            "#___gcse_0 > div > div > div > div.gsc-wrapper > div.gsc-resultsbox-visible > div > div > div.gsc-expansionArea > div:nth-child(1) > div.gs-webResult.gs-result > div.gsc-thumbnail-inside > div > a")
        print(google_result)
        found_url = google_result.get_attribute("href")
        em = display_search(found_url, 3)
        await ctx.send(content=None, embed=em)
    else:
        print("else")
        print(search_type)
        await ctx.send("I couldn't find any results, check your spelling and your brain before trying again")

    print(time.clock()-start)
@client.command()
async def help(ctx):
    em2 = discord.Embed(
        title="Possible Commands",
        color=discord.Colour.purple()
    )

    em2.add_field(name="!stats", value="Provides player information such as: Guild. Faction, Race, Class, Level, Average Item level. \n Example: !stats CharacterName Realm", inline=False)
    em2.add_field(name="!todaywow",value="Provides BFA World Boss and Emissary Quest information from WoWHead.", inline=False)
    em2.add_field(name="!search", value="Searches WoWHead for guides related to your search. Search can be for any item, equipment, raid, etc. I will try to give you the top results, but if that fails I will give the most relevant link or guide\n Example: !search uncorrupted voidwing", inline=False)
    await ctx.send(content=None, embed=em2)

def get_thumbnail(realm,character_name):
    r = requests.get("https://us.api.blizzard.com/profile/wow/character/"+realm +"/"+character_name+"/character-media",
                     params={"namespace": "profile-us", "locale": "en_US", "access_token": access_token})
    media = json.loads(r.text)
    img = media["assets"][0]["value"]
    #different possible views
    return img

def display_stat(data, img):
    # Name, Race, Class, Level, Average Item Level
    print(data)
    if data["faction"]["name"] == "Horde":
       descript= "What we do now, we do for the Horde, both of us."
    else:
        descript= "For the Alliance!"
    em = discord.Embed(
        title=data["name"],
        type="rich",
        description=descript,
        colour=discord.Colour.red()
    )
    em.set_thumbnail(url=img)

    em.add_field(name="Faction", value=data["faction"]["name"], inline=True)
    em.add_field(name="Race", value =data["race"]["name"], inline=True)
    if "guild" in data:
        em.add_field(name="Guild", value=data["guild"]["name"], inline=True)
    em.add_field(name="Class", value=data["character_class"]["name"], inline=True)
    em.add_field(name="Level", value=data["level"], inline=True)
    em.add_field(name="Average Item Level", value=data["average_item_level"], inline=True)
    em.set_footer(text="       ")

    return em

def display_search(data, search_type):
    print(data)
    if search_type == 0:
        descri = "These are the top search results"
    elif search_type == 1:
        descri = "These are the highlights of my search"
    elif search_type == 2:
        descri = "I pulled the guides, click the Main Link for more information"
    elif search_type == 3:
        descri = "These searches might be what you are looking for"


    em2 = discord.Embed(
        title="Search Results",
        description=descri,
        color=discord.Colour.green()
    )
    if search_type == 3:
        em2.add_field(name="Try this", value=data, inline=False)
        return em2
    else:
        for i, n in enumerate(data):
            em2.add_field(name=data[i]["name"], value=data[i]["link"], inline=False)
        return em2


client.run(DISCORD_TOKEN)
