import math
import os

import inflect
from dotenv import load_dotenv

millnames = ['','K','M','B','T']
p = inflect.engine()

load_dotenv()
gid = int(os.getenv("GID_TOKEN"))

crew = {
    "oishi": ["Secretly Satoshi", "Dirty $MILK whore", "I can't tell you, he's my boss", "Charles asks him for CNFT recommendations"],
    "plxce": ["whatever GC clays floor is", "the one who started the cocoloco pump", "Rank 1 of Chilled Kongs", "$MILK"],
    "swaggins": ["MOON", "dad?", "the sad state of the vaping industry", "he will take us to the moon"],
    "banch": ["a few plantains", "Spacebudz floor", "definitely not a BCRC fan", "The key to success for CNFTs is basing your decisions on whatever anyone with over 1k followers says. This is how you become rich."],
    "zeru": ["A week nonstop of giveaway winnings", "ABHS in 2022", "Handies floor", "no really, this guy wins giveaways nonstop", "the one who started the ada egg pump", "THE SENSEI", "69 Million XMR"],
    "jdavitt": ["rocket league diamond champ", "the value of cardsafe(no, really)", "who knows how nice his trading card stash truly is?", "ADA Homes floor"],
    "minshew": ["8008.135 ETH", "...buttheads floor, what else did you expect?", "/efloor buttheads", "THIS GUY ONLY WHALES ON BUTTHEADS", "buttheads w/ dudewipe combo"],
    "anthony": ["2,500,000,000 ADA", "$14,000,000,000", "9,441 ETH", "This guy is big money. No jokes."],
    "juan": ["69k ETH + a few little lemon friends", "<a:licktoes:944253276185043015>", "ROBOROBO", "He technically owns a Berry"],
    "donvts": ["first ask, how old is plxce's mom?", "this dude lives in Japan, BALLER", "wasn't his name donuts just a few days ago?", "ask Plxce's mom"],
    "chisberg": ["I would write a bunch of things with proper linespaces\n\n but I'm a dumb bot", ":eyes:", ":eyes:\n\n:eyes:", "homie is probably set, he good!"],
    "carlucio": ["Cardano village floor", "this dude whales in everything", "he's probably smarter than me"],
    "jrod": ["halo kong floor", "upcoming developer - aka he rich like my master", "the chilliest degen of them all", "10,000,000,000 ADA"],
    "dad?": ["dad isn't coming home Timmy", "Timmy, I told you, he is not coming home!", "TIMMY I CAN'T HANDLE YOU ASKING ANYMORE"],
    "bruce": "Fuck him",
    "0verdrip": ["MOONING :peach:", "Drapes floor in 2024", "always MOONING :peach:", ":peach:"],
    "goofy": ["THIS MFER MINTED THULU, POUR ONE OUT", "his cool name should be worth some ADA", "get the goofycrisp ADAHandle and sell it to him!"],
    "doczero": ["-5 ADA, this mfer owes money to the blockchain!", "smooth yeti's floor", "he lost a giveaway where he was the only one who entered", "the price of a moussaka dish"],
    "floki": ["unicorn kong floor - THIS MFER BALLIN", "degen toonz at the end of 2022", "probably 2,000,000 ADA"]
}

shortcuts = {
    "bcrc": "bosscatrocketclub",
    "bg": "benjaminsgroup",
    "carda": "cardastationland",
    "ck": "chilledkongs",
    "clays": "claynationbyclaymates",
    "clumsy": "clumsyghosts",
    "corn": "cornucopias-bubblejett-sprinter2022",
    "cwar": "cardanowarriors",
    "dcc": "degencryptoclub",
    "drapes": "derpapes",
    "gcclays": "claynationxgoodcharlottebyclaymates",
    "heartbreakclub": "theheartbreakclub",
    "mek" : "mekanismgenesisoverexposed",
    "pom": "petbotoptimizationmodule",
    "pxlz": "deadpxlz",
    "rr2": "ragingredsseason2",
    "soho": "sohokids",
    "ue": "unboundedearth",
    "unsigs": "unsigned_algorithms",
    "ubuc" : "uglyboysxuglycommunity",
    "yetis": "smoothyetimountainclub",
    "blockowls2": "blockowls-plutuscollection",
}

shortcuts_eth = {
    "bayc": "boredapeyachtclub",
    "buttheads": "buttheads-real",
    "degentoonz": "degentoonz-collection",
    "lemons": "little-lemon-friends",
    "soulz" : "soulz-monogatari7777",
}

shortcuts_tokens = {
    "leaf": "leaftoken",
    "sun": "sundae",
}

error_msg = {
    "cant_find" : "I'm a dumb bot and I couldn't find that.",
    "gen_error" : "WHOA there, some shit happened. ERROR.",
    "coin_cantfind" : "Nah son, that's such a shitcoin that my degen ass couldn't find. Or you wrote it wrong.",
    "opencnft_down" : "OpenCNFT is down. What else is new?"
}      

option_desc = {
    "pname" : "Enter the name of the project",
    "trait" : "Enter the trait you are looking for",
    "tname" : "Enter the name of the token"
}

random_mmm_msgs = [
    "TURN UP MORE TURN UP MORE!!!!!!", 
    "RAISE THE ROOF", 
    "OHHHHH THIS IS GETTTING GOOOOOD",
    "PARTY FCKIN HARD!",
    "DEGENS I CANT FUCKING HEAR YOU!!!",
    "@here BITCHES IT'S A CELEBRATION!",
    "PUMP IT UP, PUMP IT UP RIGHT THE FUCK NOW!",
    "P FOR PUMP LFGGG DENS!",
    "WHERE IS THE NOISE????????",
    "YOU GOTTA FUCKIN HYPE HARDER!!!",
    "GET MORE FUCKIN EXCITED - LFG!!!",
    "I SAID I CANT HEAR YOU DEGENS",
    "GIVE IT UP FOR DEGENS DEN MFERS!"
]

# dir paths
extras_path = '/home/pi/dev/extras/'

# general functions to tidy things up   
def sum_ada(lovelace):
    return lovelace * 1000000
    
def divide_ada(lovelace):
    return lovelace / 1000000
 
def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])    
