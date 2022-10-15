import datetime as dt
import logging
import os
import random
import re

import discord
import humanize
import rapidfuzz
import requests
import json
from discord.ext import commands
from dotenv import load_dotenv
from tqdm.contrib.discord import tqdm

from extras import *

load_dotenv()

# Toggle one for usage - MULA for live, MULATEST for dev
TOKEN=os.getenv("MULA_TOKEN")
#TOKEN=os.getenv("MULATEST_TOKEN")

intents = discord.Intents(messages=True, guilds=True, reactions=True)
bot = commands.Bot(command_prefix="/", intents=intents, case_insensitive=True)
BLOCKFROST_KEY={"project_id" : os.getenv("BLOCKFROST_TOKEN")}
mula_bot_img = 'https://bafybeidb6f5rr27no5ghctfbac4zktulwa4ku6rfhuardx3iwu7cvocl4q.ipfs.infura-ipfs.io/'
ipfs_base ='https://infura-ipfs.io/ipfs/'
ada = '₳'

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s - line %(lineno)d",
    datefmt='%Y-%m-%d %H:%M'
)

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()
        
    @discord.ui.button(label="Nah nvm", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()
        
class Project(commands.Cog):
    def __init__(self, name):
        self.bot = bot
        self.name = name
        self.policy_id = None

    # Checks for shortcuts in project names / crew fun sayings
    def shortcut_check(self):
        for short in shortcuts:
            rf = self.fuzzy(short)
            if rf > 90:
                return shortcuts[short]
        return self.name

    def fuzzy(self, arg):
        rf = rapidfuzz.fuzz.ratio(self.name, arg)
        return rf

    # Math operations on ADA
    def sum_ada(lovelace):
        return lovelace * 1000000
        
    def divide_ada(lovelace):
        return int(lovelace / 1000000)

    def tidy_date(dirty):
        clean = dirty.replace("T", " ")
        try:
            time_obj = dt.datetime.strptime(clean, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logging.exception(f"Date given: {dirty} - {e}")
            return "Error!"
        return humanize.naturaldelta(dt.datetime.utcnow() - time_obj)

    def error_msg(self, err):
        self.payload = f"{self.name} - {error_msg[err]}"
        self.proper_name = "Error!"

    # Information provided from child classes, returns a pretty embed
    def create_msg(self):
        embed_msg = discord.Embed(title=self.command_name, color=0xf70000)
        embed_msg.set_author(name="Mula Bot - Degens Den Servant", icon_url=mula_bot_img)
        embed_msg.set_footer(text=self.footer)
        if self.project_image != None:
            embed_msg.set_thumbnail(url=f"{self.project_image}")
        else:
            embed_msg.set_thumbnail(url=mula_bot_img)
        embed_msg.add_field(name=self.proper_name,
            value=f"{self.payload}")
        return embed_msg

class Jpgstore(Project):
    # API Endpoints
    policy_end = 'https://www.jpg.store/api/policy/'
    store_link = ' https://www.jpg.store/collection/'
    opencnft_policy_end = 'https://api.opencnft.io/1/policy/'
    blockfrost_end = 'https://cardano-mainnet.blockfrost.io/api/v0/'
    jpg_collection_end = 'https://server.jpgstoreapis.com/collection/'
    jpg_policy_end = 'https://server.jpgstoreapis.com/policy/'

    # jpg.store logo
    logo = 'QmbbfCQQBuVcWkX7hJ23LVNgoXRQi4mAVzT92mmcwBvqFF'

    def __init__(self, name):
        super().__init__(name)
        self.marketplace = "jpg"
        self.footer = "Data provided by jpg.store"
        self.proper_name = None
        self.asset_id = None
        self.project_image = None
        self.command_name = None
        self.amount = None
        self.payload = None
        self.hype_flag = False
        self.channel_id = 0
        self.floor_price = None
    
    # new to set values to class directly

    def policy_lookup(self):
        self.name = Project.shortcut_check(self)
        pid_path = '/home/pi/dev/policyIDs/projects/'
        pid_list = os.listdir(pid_path)
        sorted_pid_list = sorted(pid_list)
        for project in sorted_pid_list:
            fuzz = self.fuzzy(project.replace(" ","").lower())
            if fuzz > 80:
                self.proper_name = project
                break
        try:
            with open(f"{pid_path}{self.proper_name}", 'r') as f:
                project_match = json.load(f)
                f.close()
        except FileNotFoundError as e:
            pass

        try:
            self.policy_id = str(project_match['policies']).strip("[']")
        except (KeyError, TypeError):
            self.policy_id = str(project_match[0]['policies']).strip("[']")
        except UnboundLocalError as e:
            pass

        
    def lowest_floor_new(self):
        response_API = requests.get(f"{self.jpg_collection_end}{self.policy_id}/floor")
        jpg_floor_data = response_API.json()
        self.payload = str(Project.divide_ada(int(jpg_floor_data['floor'])))
        self.project_image = self.get_cnft_img()

    # end new functions

    def get_cnft_img(self):
        try:
            response_API = requests.get(f"{self.opencnft_policy_end}{self.policy_id}", timeout=2)
            opencnft_policy_data = response_API.json()
            if isinstance(opencnft_policy_data['thumbnail'][7:], str):
                return f"{ipfs_base}{opencnft_policy_data['thumbnail'][7:]}"
            else:
                return f"{ipfs_base}{self.logo}"
        except:
            response_API2 = requests.get(f"{self.blockfrost_end}assets/{self.asset_id}", headers=BLOCKFROST_KEY)
            blockfrost_asset_data = response_API2.json()
            return f"{ipfs_base}{blockfrost_asset_data['onchain_metadata']['image'][7:]}"

    def lowest_floor(self):
        ''' jpg.store changed apis
        response_API = requests.get(f"{self.policy_end}{self.policy_id}/listings")
        jpg_listing_data = response_API.json()
        sorted_jpg_listing_data = sorted(jpg_listing_data, key=lambda x: x['price_lovelace'])
        jpg_floor_price = str(Project.divide_ada(int(sorted_jpg_listing_data[0]['price_lovelace'])))
        self.asset_id = sorted_jpg_listing_data[0]['asset']
        '''
        response_API = requests.get(f"{self.jpg_collection_end}{self.policy_id}/floor")
        jpg_floor_data = response_API.json()
        self.floor_price = str(Project.divide_ada(int(jpg_floor_data['floor'])))
        self.project_image = self.get_cnft_img()
        if self.hype_flag == True:
            self.floor_price = int(self.floor_price) * random.randint(0,30)
            if self.floor_price == 0:
                self.floor_price = f" WAIT- NO HYPE! Your shit is at {ada}8 rugpull status."
        web_friendly_name = self.name.replace(" ", "")
        self.payload = (f"Floor price: {ada}**{self.floor_price}**\n"
        f"[jpg.store link]({self.store_link}{web_friendly_name})")

    def recent_sales(self):
        ''' jpg.store changed apis
        response_API = requests.get(f"{self.policy_end}{self.policy_id}/sales")
        jpg_sales_data = response_API.json()[0:self.amount]
        '''
        resposne_API = requests.get(f"{self.jpg_policy_end}{self.policy_id}/sales?page=1")
        jpg_sales_data = resposne_API.json()[0:self.amount]
        try:
            self.asset_id = jpg_sales_data[0]['asset_id']
            self.project_image = self.get_cnft_img()
            self.payload = ''.join([f"**{p.ordinal(int(jpg_sales_data.index(x) +1))}** {x['display_name']} "
            f"**|** Price: {ada}**{str(Project.divide_ada(int(x['price_lovelace'])))}** "
            f"- Purchased: **{Project.tidy_date(str(x['confirmed_at'])[:-10])}**\n" for x in jpg_sales_data])
        except IndexError as e:
            logging.error(e)
            self.error_msg('cant_find')
            self.create_msg()

    def ocnft_ath_sales(self):
        try:
            response_API = requests.get(f"{self.opencnft_policy_end}{self.policy_id}/transactions?order=price", timeout=3)
        except requests.exceptions.Timeout as e:
            logging.error(f"Name given: {self.name} - {e}")
            self.error_msg('opencnft_down')
            return self.create_msg()
        opencnft_ath_data = response_API.json()['items'][0:10]
        self.payload = ''.join([f"**{p.ordinal(int(opencnft_ath_data.index(x) +1))}** {x['unit_name']} - Price: ₳**{str(int(divide_ada(x['price'])))}**\n" for x in opencnft_ath_data])

    def retrieve_floor_price(self):
        if self.hype_flag == True:
            self.command_name = "HYPE Floor"
        else:
            self.command_name = "Floor"
        try: 
            self.policy_lookup()
            self.lowest_floor()
            logging.info(f"Serving command: {self.command_name} - {self.proper_name}")
        except (TypeError, UnboundLocalError, KeyError) as e:
            logging.error(f"Name given: {self.name}")
            self.error_msg('cant_find')
        return self.create_msg()

    def retrieve_recent_sales(self):
        self.command_name = f"Last {self.amount} Sale{''if self.amount == 1 else 's'}"
        try:
            self.policy_lookup()
            self.recent_sales()
            logging.info(f"Serving command: {self.command_name} - {self.proper_name}")
        except TypeError as e:
            logging.error(f"Name given: {self.name} - {e}")
            self.error_msg('cant_find')
        return self.create_msg()

    def retrieve_trait_floor_price(self, trait):
        self.command_name = "Trait - Floor"
        response_API = requests.get(f"{self.jpg_policy_end}{self.policy_id}/listings")
        jpg_listing_data = response_API.json()
        sorted_jpg_listing_data = sorted(jpg_listing_data, key=lambda x: x['price_lovelace'])
        count = 1
        with tqdm(total=len(sorted_jpg_listing_data), token=TOKEN, channel_id=self.channel_id, desc="Progress") as pbar:
            for asset in sorted_jpg_listing_data:
                response_API2 = requests.get(f"{self.blockfrost_end}assets/{asset['asset']}", headers=BLOCKFROST_KEY)
                blockfrost_asset_data = response_API2.json()
                if trait.lower() in str(blockfrost_asset_data['onchain_metadata']).lower():
                    lowest_trait_floor, self.project_image = asset, f"{ipfs_base}{blockfrost_asset_data['onchain_metadata']['image'][7:]}"
                    self.payload = (f"Trait: **{trait.title()}**\n"
                    f"Floor price: {ada}**{str(int(divide_ada(lowest_trait_floor['price_lovelace'])))}**")
                    pbar.update(len(sorted_jpg_listing_data) - count + 1)
                    pbar.set_description("Match Found!")
                    pbar.close()
                    break
                else:
                    pbar.update(1)
                    count += 1
        return self.create_msg()

    def retrieve_ath_project(self):
        try:
            self.policy_lookup()        
            self.project_image = self.get_cnft_img()
            self.command_name = f"ATH Sales for: {self.proper_name}"
            self.footer = "Data provided by opencnft.io"
            self.ocnft_ath_sales()
            logging.info(f"Serving command: {self.command_name} - {self.proper_name}")
        except KeyError as e:
            logging.error(f"Name given: {self.name} - {e}")
            self.error_msg('cant_find')
        return self.create_msg()

class Token(commands.Cog):
    museliswap_ticker_end = 'http://analytics.muesliswap.com/ticker'
    museliswap_summary_end = 'http://analytics.muesliswap.com/summary'
    museliswap_tokeninfo_end = 'https://orders.muesliswap.com/tokens-info'
    museliswap_logo_end = 'https://ada.muesliswap.com/'
    museliswap_logo = 'https://ada.muesliswap.com/images/logoLarge.png'

    def __init__(self, token):
        self.bot = bot
        self.token = token
        self.token_logo = Token.museliswap_logo
        self.command_name = None
        self.token_proper_name = None
        self.policy_id = None
        self.token_last_price = None
        self.token_marketcap = None
        self.token_volume = None
        self.emoji_indicator = None
        self.ticker_data = None
        self.summary_data = None
        self.tokeninfo_data = None
        self.filtered_summary_data = None
        self.payload = None
        self.footer = "Data provided by museliswap.com"

    def shortcut_check(self):
        if self.token.lower() in shortcuts_tokens: 
            self.token = shortcuts_tokens[self.token.lower()]

    def sum_ada(price):
        return price * 1000000

    def error_msg(self, err):
        self.payload = f"{self.token} - {error_msg[err]}"
        self.proper_name = "Error!"

    def museliswap_data_load(self):
        response_API = requests.get(self.museliswap_ticker_end)
        self.ticker_data = response_API.json()
        response_API2 = requests.get(self.museliswap_summary_end)
        self.summary_data = response_API2.json()
        response_API3 = requests.get(Token.museliswap_tokeninfo_end)
        self.tokeninfo_data = response_API3.json()

    def filter_results(self):
        self.shortcut_check()
        r = re.compile(".*"+self.token+"_ADA", re.IGNORECASE)
        ticker_results = list(filter(r.match, self.ticker_data))
        filtered_summary_data = [x for x in self.summary_data if ticker_results[0] in x['trading_pairs']]
        policy_id = str(ticker_results[0]).strip().split(".",1)[0]
        token_last_price = self.ticker_data[str(ticker_results[0])]['last_price']
        emoji_indicator = ":chart_with_upwards_trend:+" if filtered_summary_data[0]['price_change_percent_24h'] > 0 else ":chart_with_downwards_trend:"
        if 'e' in str(token_last_price):
            token_last_price = sum_ada(token_last_price)
        token_volume = self.ticker_data[str(ticker_results[0])]['quote_volume']
        return filtered_summary_data, policy_id, token_last_price, emoji_indicator, token_volume

    def token_extra_stats(self):
        token_data = [x for x in self.tokeninfo_data if self.policy_id in x['policyId']]
        try:
            token_marketcap = float(self.token_last_price) * float(token_data[0]['circulatingSupply'])
        except ValueError:
            token_marketcap = 0
        except:
            token_marketcap = float(self.token_last_price) * float(token_data[0]['totalSupply'])
        if 'e' in str(self.token_last_price): self.token_last_price = 0
        try:
            if token_data[0]['image'].startswith("http"): token_logo = token_data[0]['image']
            else: token_logo = self.museliswap_logo_end + token_data[0]['image']
        except IndexError:
            pass
        token_proper_name = token_data[0]['name']
        return token_marketcap, token_proper_name, token_logo

    def create_msg(self):
        siren_emoji = ":rotating_light:"
        embed_msg = discord.Embed(title="Token Stats", color=0xf70000)
        embed_msg.set_author(name="Mula Bot - Degens Den Servant", icon_url=mula_bot_img)
        embed_msg.set_footer(text=self.footer)
        embed_msg.set_thumbnail(url=self.token_logo)
        embed_msg.add_field(name=self.token_proper_name, value=self.payload)
        if self.token_last_price == 0:
            embed_msg.add_field(name=f"{siren_emoji} SHIT COIN ALERT {siren_emoji}", value="Son, this coin is straight SHIT. Sorry. Do better?", inline=False)
        return embed_msg

    def retrieve_token_stats(self):
        self.museliswap_data_load()
        try:
            self.command_name = "Toke"
            self.filtered_summary_data, self.policy_id, self.token_last_price, self.emoji_indicator, self.token_volume = self.filter_results()
            self.token_marketcap, self.token_proper_name, self.token_logo = self.token_extra_stats()
            self.payload = (f"Last Price: ₳ **{str(format(self.token_last_price, 'g'))}** {self.emoji_indicator} **{str(self.filtered_summary_data[0]['price_change_percent_24h'])[:5]}%** \n"
            f"Market Cap: ₳**{str(millify(self.token_marketcap))}** \n"
            f"Volume: ₳**{str(millify(self.token_volume))}**")
            logging.info(f"Serving command: {self.command_name} - {self.token_proper_name}")
        except (IndexError, TypeError, ValueError) as e:
            logging.error(f"Name given: {self.token} - {e}")
            self.error_msg('coin_cantfind')
        return self.create_msg()