import asyncio
import datetime as dt
import logging
import os
from pydoc import describe
import random
import sqlite3

import discord
import requests
from discord.commands import Option
from discord.ext import commands, tasks
from dotenv import load_dotenv

from classes import *
from extras import random_mmm_msgs, extras_path
from extras import *

load_dotenv()

# Toggle one for usage - MULA for live, MULATEST for dev
TOKEN=os.getenv("MULA_TOKEN")
#TOKEN=os.getenv("MULATEST_TOKEN")

opensea_end = 'https://api.opensea.io/api/v1/collection/'

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s - line %(lineno)d",
    datefmt='%Y-%m-%d %H:%M'
)

intents = discord.Intents(emojis=True, messages=True, message_content=True, guilds=True, reactions=True)
bot = commands.Bot(command_prefix="/", intents=intents, case_insensitive=True)
am = discord.AllowedMentions(everyone = True, users = True)

class EpochTimer(commands.Cog):
    blockfrost_base = 'https://cardano-mainnet.blockfrost.io/api/v0/'
    blockfrost_policy_base = 'https://cardano-mainnet.blockfrost.io/api/v0/assets/policy/'

    def __init__(self):
        self.bot = bot
        self.channel_id = 941428920488718406
        self.current_epoch = None
        self.epoch_countdown.start()
        
    async def on_ready(self):
        pass

    @tasks.loop(minutes=30)
    @bot.event
    async def epoch_countdown(self):  
        # load the epoch file which has the end date from Blockfrost
        try:
            check_file = os.stat("epoch_end.txt").st_size
        except OSError:
            f = open("epoch_end.txt", "w").close()
            check_file = os.stat("epoch_end.txt").st_size
        
        # check if the file is empty, if not, request the date from Blockfrost
        if check_file == 0:
            response_API = requests.get(f"{self.blockfrost_base}epochs/latest", headers=BLOCKFROST_KEY)
            blockfrost_epoch = response_API.json()
            f = open("epoch_end.txt", "w")
            f.write(str(blockfrost_epoch['end_time']) + "\n" + str(blockfrost_epoch['epoch']))
            f.close()
            logging.info(f"Loaded information for Epoch {blockfrost_epoch['epoch']}")
            
        if self.current_epoch == None:
            try:
                f = open("epoch_end.txt", "r")
                epoch_info = f.readlines()
                f.close()
                self.current_epoch = int(epoch_info[1])
            except Exception as e:
                logging.error(e)
                response_API = requests.get(f"{self.blockfrost_base}epochs/latest", headers=BLOCKFROST_KEY)
                blockfrost_epoch = response_API.json()
                self.current_epoch = int(blockfrost_epoch['epoch'])
        
        # open the file and load the information while removing whitespace, for comparison
        f = open("epoch_end.txt", "r")
        epoch_info = f.readlines()
        f.close()
        epoch_end_time = epoch_info[0].strip()
        epoch_end_utc = dt.datetime.utcfromtimestamp(int(epoch_end_time))
        current_utc = dt.datetime.utcnow()
        
        # if current time is greater then epoch end time, the bot will announce a new epoch
        # and then will clear the text file, so next time the loop runs, it can get the next epoch end
        if epoch_end_utc < current_utc:
            annoucements_channel = bot.get_channel(self.channel_id)   
            new_epoch = self.current_epoch + 1
            await annoucements_channel.send(("@everyone\n" 
            "<a:sirenred:944494985288515644> **A NEW EPOCH HAS BEGUN!** <a:sirenred:944494985288515644> \n"
            f"We are now on **Epoch {new_epoch}** \n"
            "Don't forget your Dripdropz at https://dripdropz.io/"), allowed_mentions=am)
            open("epoch_end.txt", "w").close()
            
    @epoch_countdown.before_loop
    async def before_epoch_countdown(self):
        logging.info("Starting for Epoch Countdown")
        await self.bot.wait_until_ready()   

def create_msg(mp, maintitle):
    jpg_footer = "Data provided by jpg.store"
    opencnft_footer = "Data provided by opencnft.io"
    opensea_footer = "Data provided by opensea.io"
    museliswap_footer  = "Data provided by museliswap.com"
    
    new_embed_msg = discord.Embed(title=maintitle, color=0xf70000)
    new_embed_msg.set_author(name="Mula Bot - Degens Den Servant", icon_url=mula_bot_img)
    match mp:
        case 'jpg':
            new_embed_msg.set_footer(text=jpg_footer)
        case 'opencnft':
            new_embed_msg.set_footer(text=opencnft_footer)
        case 'opensea':
            new_embed_msg.set_footer(text=opensea_footer)
        case 'museliswap':
            new_embed_msg.set_footer(text=museliswap_footer)
        case _:
            new_embed_msg.set_footer(text="Data brought to you by ME!")
    return new_embed_msg

def error(name, err):
    header = "Error!"
    payload = f"{name} - {error_msg[err]}"
    return header, payload

@bot.event
async def on_ready( ):
    logging.info("Mula Bot is BACK!")

# CommandNotFound handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


# Help features   
@bot.slash_command(name="wtf", description="See commands available. Also, only you can see this. Won't spam chat. PROMISE.", guild_ids=[gid])
async def wtf(ctx):
    embed_msg = create_msg("Oishi", "You need some help!")
    embed_msg.set_thumbnail(url='https://bafybeidb6f5rr27no5ghctfbac4zktulwa4ku6rfhuardx3iwu7cvocl4q.ipfs.infura-ipfs.io/')
    embed_msg.add_field(name="Commands available", value=("**/floor *<projectname>*** --> Retrieve floor \n"
    "**/traitfloor *<name> <trait>*** --> Retrieve the floor on a specific trait[DOWN] \n"
    "**/efloor *<name>*** --> Retrieve floor from ETH \n"
    "**/last *<name> <amount>*** --> Retrieve last <amount> of transactions \n"
    "**/top10 *<name>*** --> Retrieve top ten sales of project \n"
    "**/top10all** --> Retrieve top ten projects today \n"
    "**/hypefloor** --> When you need a pick me up \n"
    "**/toke *<tokenname>*** --> Gets the last price/volume from Museli\n"
    "**/shorts** --> Shows your shortcuts available for projects / tokens\n"
    "**/vibe** --> When you just need to vibe a bit\n"
    "**/addproject** --> Add a project to #upcoming-mints\n"
    "**/mmm** --> Money Mike Mode, TURN IT UP!\n"
    "**/wtf** --> This command"), inline=False)
    await ctx.respond(embed=embed_msg, ephemeral=True)
    
@bot.slash_command(name="shorts", description="See the shortcuts available with each command.", guild_ids=[gid])
async def shorts(ctx):
    embed_msg = create_msg("Oishi", "Shortcuts!")
    embed_msg.set_thumbnail(url='https://bafybeidb6f5rr27no5ghctfbac4zktulwa4ku6rfhuardx3iwu7cvocl4q.ipfs.infura-ipfs.io/')
    embed_msg.add_field(name="Cardano NFTs", value=''.join(["**" + x + "**" + " - " + shortcuts[x] + "\n" for x in shortcuts]), inline=False)
    embed_msg.add_field(name="Ethereum NFTs", value=''.join(["**" + y + "**" + " - " + shortcuts_eth[y] + "\n" for y in shortcuts_eth]), inline=True)
    embed_msg.add_field(name="Cardano Tokens", value=''.join(["**" + z + "**" + " - " + shortcuts_tokens[z] + "\n" for z in shortcuts_tokens]), inline=True)
    await ctx.respond(embed=embed_msg, ephemeral=True)

# jpg.store commands
@bot.slash_command(name="floor", description="Retrieve the floor price", guild_ids=[gid])
async def floor(ctx, *, name: Option(str, option_desc['pname'])):
    await ctx.defer()
    if name.lower() in crew:
        await ctx.respond(f"{name.title()} - {random.choice(crew[name.lower()])}")
    else:
        cnft_project = Jpgstore(name.lower())
        await ctx.respond(embed=cnft_project.retrieve_floor_price())

@bot.slash_command(name="last", description="Retrieve the last # sales made", guild_ids=[gid])
async def last(
    ctx, 
    *, 
    name: Option(str, option_desc['pname']), 
    amount: Option(int, "Enter how many sales you wish to see", min_value=1, max_value=10, default=5)
):
    await ctx.defer()
    cnft_project = Jpgstore(name.lower())
    cnft_project.amount = int(amount)
    await ctx.respond(embed=cnft_project.retrieve_recent_sales())

@bot.slash_command(name="hypefloor", description="When you need to feel really really good", guild_ids=[gid])
async def hypefloor(ctx, *, name: Option(str, option_desc['pname'])):
    await ctx.defer()
    if name.lower() in crew:
        await ctx.respond(f"{name.title()} - {random.choice(crew[name.lower()].upper())}")
    else:
        cnft_project = Jpgstore(name.lower())
        cnft_project.hype_flag = True
        await ctx.respond(embed=cnft_project.retrieve_floor_price())

@bot.slash_command(name="traitfloor", description="Retrieve a trait's floor price", guild_ids=[gid])
async def traitfloor(
    ctx,
    *,
    name: Option(str, option_desc['pname']), 
    trait: Option(str, option_desc['trait'])
):
    await ctx.defer()
    await ctx.respond("Nah this is down for now.")
''' down till further notice - jpg.store
    cnft_project = Jpgstore(name.lower())
    og_msg = "You want the floor of a trait? Alright, lemme get started."
    cnft_project.channel_id = ctx.channel.id
    try:
        cnft_project.proper_name, cnft_project.policy_id = Jpgstore.policy_lookup(cnft_project)
    except:
        logging.exception(f"Name given: {name} | Trait given: {trait}")
        cnft_project.command_name = "Trait - Floor"
        cnft_project.error_msg('cant_find')
        await ctx.respond(embed=cnft_project.create_msg())
        return  
    og_msg = await ctx.respond(f"You requested **{cnft_project.proper_name}** with the trait: **{trait}**")
    await ctx.respond(embed=cnft_project.retrieve_trait_floor_price(trait))
    await og_msg.edit(f"{ctx.author.mention}, I found the results for your {cnft_project.proper_name} - {trait}. BYE!", allowed_mentions=am)
'''

@bot.slash_command(name="top10", description="Retrieve the Top 10 ATH sales on a project", guild_ids=[gid])
async def top10(ctx, *, name: Option(str, option_desc['pname'])):
    await ctx.defer()
    cnft_project = Jpgstore(name.lower())
    await ctx.respond(embed=cnft_project.retrieve_ath_project())

@bot.slash_command(name="top10all", description="Retrieve the Top 10 projects today on OpenCNFT", guild_ids=[gid])
async def top10all(ctx):
    await ctx.defer()
    embed_msg = create_msg('opencnft', 'Top 10 Today')
    try:
        response_API = requests.get('https://api.opencnft.io/1/rank?window=24h', timeout=3)
        opencnft_top10all_data = response_API.json()['ranking'][0:10]
        msg_header = "Project Name - Volume - Floor Price"
        payload = ''.join([f"**{p.ordinal(int(opencnft_top10all_data.index(x) +1))}** {x['name']} - **Volume(24hr): ₳**{millify(x['volume'])} - **Floor: ₳**{x['floor_price']}\n" for x in opencnft_top10all_data])    
        logging.info(f"Serving command: Top 10 All ")
    except Exception as e:
        logging.error(e)
        msg_header, payload = error("Womp womp", 'opencnft_down')
    embed_msg.add_field(name=msg_header, value=payload, inline=False)
    await ctx.respond(embed=embed_msg)

# openseas.io commands - merge efloor & floor
@bot.slash_command(name="efloor", description="Retrieve the floor on an ETH project", guild_ids=[gid])
async def efloor(ctx, *, name: Option(str, option_desc['pname'])):
    await ctx.defer()
    embed_msg = create_msg('opensea', 'Floor')  
    if name.lower() in shortcuts_eth: name = shortcuts_eth[name.lower()]
    response_API = requests.get(f"{opensea_end}{name}/stats")
    opensea_stats_data = response_API.json()
    response_API2 = requests.get(f"{opensea_end}{name}")
    opensea_project_data = response_API2.json()
    try:
        name, img = opensea_project_data['collection']['name'], opensea_project_data['collection']['image_url']
        payload = f"Floor price: Ξ**{opensea_stats_data['stats']['floor_price']}**"
        embed_msg.set_thumbnail(url=img)
    except KeyError as e:
        logging.error(f"Name given: {name} - {e}")
        name, payload = error(name.title(), 'cant_find')
    
    embed_msg.add_field(name=name, value=payload)
    await ctx.respond(embed=embed_msg)

# museliswap.com commands /  tokens
@bot.slash_command(name="toke", description="Retrieve stats for a token on MuseliSwap", guild_ids=[gid])
async def toke(ctx, *, toke: Option(str, option_desc['tname'])):
    await ctx.defer()
    token_request = Token(toke)
    await ctx.respond(embed=token_request.retrieve_token_stats())

# fun commands
@bot.slash_command(name="addproject", description="Add a new project to Upcoming Mints!", guild_ids=[gid])
async def addproject(ctx):
    def check(user):
        return user.author == ctx.author
        
    logging.info(f"Serving command: Add Project")
    # Setting up the questions & prompts
    embed_msg = create_msg("Oishi", "Upcoming Mint")
    embed_msg.add_field(name="So you want to add a project's upcoming mint?", value=(":notepad_spiral: **Instructions**:\n" 
    "This function is to create a new listing in upcoming-mints!\n"
    "If you continue, I will ask you **four questions** regarding the upcoming mint.\n"
    "**When you click continue**, I will take the next four things you type and **delete them**.\n"
    "If you **do not** wish to continue, please click cancel!\n"
    "Please **continue** or **cancel**."))
    embed_msg1 = create_msg("Oishi", "Upcoming Mint")
    embed_msg1.add_field(name="Upcoming Project Mint", value=("Please type the **project's name**"))
    embed_msg2 = create_msg("Oishi", "Upcoming Mint")
    embed_msg2.add_field(name="Upcoming Project Mint", value=("When is it **happening**?"))
    embed_msg3 = create_msg("Oishi", "Upcoming Mint")
    embed_msg3.add_field(name="Upcoming Project Mint", value=("What is the **price**?"))
    embed_msg4 = create_msg("Oishi", "Upcoming Mint")
    embed_msg4.add_field(name="Upcoming Project Mint", value=("What is the **discord link**?\nIf you don't have a link, just write **skip**"))
    embed_msg_complete = create_msg("Oishi", "Upcoming Mint")
    embed_msg_complete.add_field(name="Finished!", value="Thank you for adding the upcoming mint!\nYou can see it now in upcoming-mints")
    embed_msg_cancel = create_msg("Oishi", "Upcoming Mint")
    embed_msg_cancel.add_field(name="Cancelling", value="TF you summoned me for then????")
    
    # For the first prompt with buttons
    view = Confirm()
    confirmation = await ctx.respond(embed=embed_msg, ephemeral=True, view=view)
    await view.wait()
    
    if view.value is True:
        view.clear_items()
        # Asking the questions and saving the answers, deleting after
        questions = await ctx.respond(embed=embed_msg1, ephemeral=True)
        new_project_name = await bot.wait_for('message', check=check)
        await new_project_name.delete()
        await questions.edit(embed=embed_msg2)
        await asyncio.sleep(1)
        new_project_date = await bot.wait_for('message', check=check)
        await new_project_date.delete()
        await questions.edit(embed=embed_msg3)
        await asyncio.sleep(1)
        new_project_price = await bot.wait_for('message', check=check)
        await new_project_price.delete()
        await questions.edit(embed=embed_msg4)
        await asyncio.sleep(1)
        new_project_discord = await bot.wait_for('message', check=check)
        if new_project_discord.content.lower() == "skip":
            await new_project_discord.delete()
            new_project_discord.content = "No discord link provided"
        else:
            await new_project_discord.delete()
            
       # Posting the new project
        await questions.edit(embed=embed_msg_complete)
        upcoming_mints_channel = bot.get_channel(942488274138714152)
        await upcoming_mints_channel.send(("Information provided by: " + str(ctx.author.mention) + "**\n" + str(new_project_name.content) + "** \n"
        ":calendar_spiral: - " + str(new_project_date.content) + "\n"
        ":moneybag: - **" + str(new_project_price.content) + "**\n" + str(new_project_discord.content)))
        
    else:
        await ctx.respond(embed=embed_msg_cancel, ephemeral=True)

@bot.slash_command(name="vibe", description="Just vibe", guild_ids=[gid])
async def vibe(ctx):
    await ctx.defer()
    logging.info(f"Serving command: Vibe ")
    await ctx.respond("Just be polite and life's good.")

plxce_check = False
@bot.slash_command(name="plxcepowpow", description="Is Plxce acting up again?", guild_ids=[gid])
async def plxcepowpow(
    ctx,
    is_he: Option(str, "Is he? Yes - On, No - Off, Shh - Stealth Special", choices=["yes", "no", "shh"])
    ):
    logging.info(f"Serving command: Plxce pow pow ")
    global plxce_check
    if ctx.author.id == 382652120421105677:
        await ctx.respond("Nice try bitch")
    elif is_he == "yes":
        plxce_check = True
        await ctx.respond("<@382652120421105677> STOP ACTING UP")
    elif is_he == "no":
        plxce_check = False
        await ctx.respond("<@382652120421105677> ok, you good now.")
    elif is_he == "shh":
        plxce_check = True
        await ctx.respond("Turning on Plxce Pow Pow!", ephemeral=True) 

money_mike_mode = False
@bot.slash_command(name="mmm", description="TURN IT UP DEGENS!!", guild_ids=[gid])
async def mmm(
    ctx,
    turn_up: Option(str, "ARE WE READY TO TURN TF UP??", choices=["yes", "no"])
    ):
    logging.info(f"Serving command: Money Mike Mode ")
    global money_mike_mode
    if turn_up == "yes":
        money_mike_mode = True
        await ctx.respond("AYYY WE TURNIN UP IN THIS BITCH!!! LFG!!! MONEY MIKE MODE ON!")
    elif turn_up == "no":
        money_mike_mode = False
        await ctx.respond("ok we done")

@bot.slash_command(name="shouldplxcebuyit", description="I can answer this question!", guild_ids=[gid])
async def shouldplxcebuyit(ctx):
    await ctx.respond("**FUCK NO**")

# Functions for Random mmm stuff
async def gif_time(msg):
    random_gif = random.choice(os.listdir("./img/"))
    with open(f'./img/{random_gif}', 'rb') as gif:
        picture = discord.File(gif)
        return await msg.channel.send(file=picture)

@bot.listen("on_message")
async def on_message(msg, guild_ids=[gid]):
    if msg.author == bot.user: return
    
    #Twitter alarms / copy to Twitter channels
    twitter_alarms = ['a:sirenred:944494985288515644', 'a:sirenblue:944494579409883157', 'a:sirengreen:944494579770593290', 'a:sirenpurple:944494579544117279', 'a:sirenred2:944494548325912617']
    twitter_channel = bot.get_channel(944095401194172427)
    zeru_channel = bot.get_channel(941847130983759872)
    if 'https://twitter.com' in msg.content.lower():
        if msg.author.id == 503807404648038410:
            await zeru_channel.send("**" + "NEW FIRE POSTED BY: **" + str(msg.author.mention) + "\n" + str(msg.content))
        else:
            await twitter_channel.send("**" + "NEW FIRE POSTED BY: **" + str(msg.author.mention) + "\n" + str(msg.content))
        await asyncio.sleep(1)
        for emoji in twitter_alarms: await msg.add_reaction(emoji)

    # Plxce Beats
    if 'drop the beat' in msg.content.lower():
        with open(f"{extras_path}herewego.gif", 'rb') as gif:
            here_we_go = discord.File(gif, filename="here_we_go.gif")
            await msg.channel.send(file=here_we_go)
        with open(f"{extras_path}brunch_for_dinner.mp3", 'rb') as beat:
            brunch = discord.File(beat, filename="brunch_for_dinner.mp3")
            await msg.channel.send(file=brunch)
    
    # Plxcepowpow check
    global plxce_check
    plxce_reacts = ['a:madbeat:946942169476911114', 'a:therethere:949850879803138101', 'a:drunkclown:949850910136361030', 'a:hellno:949852087410376735', 'a:shook:949850848488468490', 'a:angryaf:949851841146019890', 'a:pepepee:949849956569735229']
    if plxce_check is True:
        if msg.author.id == 382652120421105677:
            for emoji in plxce_reacts: await msg.add_reaction(emoji)

    # MoneyMikeMike check
    global money_mike_mode
    mmm_reacts = ['\U0001f17f', '\U0001f48e', '\U0001f9f9', '\u2665', '\U0001f493', '\U0001f440', '🥵', '\u26A0', '\u2757', '\u203C', '🚀', '💀', '🍻', '🎉', '📈', '🚷', ':BigMoneyOnTuesday:945168351716581376', 'a:kanyedance:949852333012058152', 'a:thinkaf:949853381449637888']
    
    if money_mike_mode is True:
        i = 0
        reacts_num = random.randint(1,8)
        for i in range(reacts_num):
            mmm_reacts_msg = mmm_reacts
            react = random.choice(mmm_reacts_msg)
            mmm_reacts_msg.remove(react)
            await msg.add_reaction(react)
        turn_up = random.randint(1,20)
        match turn_up:
            case 1:
                await msg.channel.send(random.choice(random_mmm_msgs))
            case 4:
                await gif_time(msg)
            case 8:
                await gif_time(msg)
            case 11:
                await msg.channel.send(random.choice(random_mmm_msgs))
            case 12:
                await msg.channel.send(random.choice(random_mmm_msgs))
            case 13:
                 await gif_time(msg)
            case 17:
                await msg.channel.send(random.choice(random_mmm_msgs))
            case 19:
                 await gif_time(msg)

epoch_countdown_task = EpochTimer()
bot.run(TOKEN)
