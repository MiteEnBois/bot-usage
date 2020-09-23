import os
import discord
import time
import sys
import math
import re
from random import shuffle, randint
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

# ----------------------------- SETUP VARIABLES GLOBALES ET BOT

global COOLDOWN, DUREE
DUREE = 10
COOLDOWN = 0

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PASSWORD = os.getenv('PASSWORD')

bot = commands.Bot(command_prefix=';')

# ----------------------------- FONCTIONS UTILITAIRES


@bot.command(name='ping', help='Pong!')
async def ping(ctx):
    await ctx.send("Pong!")

# ----------------------------- COMMANDES


@bot.command(name='saucisson', help='Pong!')
async def saucisson(ctx, *arr):
    limit = 64
    num = randint(0, 99)
    if ctx.author.id == 243312493730988032:
        num -= 20
    if num >= limit:
        await ctx.send(f"{' '.join(arr)} est mieux que le saucisson")
    else:
        await ctx.send(f"{' '.join(arr)} est moins bien que le saucisson")


@bot.command(name='boule', help='Pong!')
async def boule(ctx, *arr):
    boule = ["Essaye plus tard", "Essaye encore", "Pas d'avis", "C'est ton destin", "Le sort en est jeté", "Une chance sur deux", "Repose ta question", "D'après moi oui", "C'est certain",
             "Oui absolument", "Tu peux compter dessus", "Sans aucun doute", "Très probable", "Oui", "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver", "N'y compte pas", "Impossible"]
    rempl = {
        "mon": "ton",
        "me": "te",
        "ma": "ta",
        "mes": "tes",
        "j": "t",
        "je": "tu",
        "suis": "es",
        "ai": "a",

    }

    str = ' '.join(arr).lower()
    for x in rempl:
        # str = str.replace(x, rempl[x])
        # sub = f"\b{x}\b"
        str = re.subn(rf"\b{x}\b", rempl[x], str)[0]
    if str[-1] != '?':
        if str[-1] != ' ':
            str += ' '
        str += '?'
    await ctx.send(f"{str.capitalize()} : 🎱**{boule[randint(0, 19)]}**🎱")


@bot.command(name='bouleuh', help='Pong!')
async def bouleuh(ctx, *arr):
    await ctx.send("Nique bouleuh tout mes potes détestent bouleuh")


@bot.command(name='usage', help='compte les messages de chaque canal dans les x derniers jours. usage: ;usage <jours(defaut 7)> <limite message(defaut 500)>')
async def usage(ctx, jours=7, lim=1000):
    datef = datetime.fromtimestamp(time.time())-timedelta(days=jours)
    ttttime = time.time()
    channels = {}

    allmsg = 0
    for cat in ctx.guild.categories:
        # if "squat" not in cat.name.lower():
        #     break
        for chan in cat.channels:
            try:
                if chan.name[0] == "_":
                    continue
                if(str(chan.type) == "text"):
                    channels[chan.id] = {
                        "name": chan,
                        "score": 0,
                        "time": 0.0
                    }
                    i = 0
                    temptime = time.time()
                    # msglist = await chan.history(limit=lim, after=datef).flatten()
                    # i = len(msglist)
                    async for message in chan.history(limit=lim):
                        if message.author == bot.user:
                            continue
                        if message.created_at <= datef:
                            break
                        i += 1
                    channels[chan.id]["score"] = i
                    delta = round((time.time()-temptime)*1000.0)
                    channels[chan.id]["time"] = delta
                    print(f"{chan} : {delta}ms")
                    allmsg += i
            except discord.errors.Forbidden:
                print("forbiden channel")
            except:
                print("Unexpected error:", sys.exc_info())
                for x in sys.exc_info():
                    print(x)
                continue
    print("---------------------------")
    sc = 1
    csv = ""
    c = {k: v for k, v in sorted(channels.items(), key=lambda item: item[1]["score"], reverse=True)}
    csv = ""
    txt = "**__UTILISATION DES CANAUX DE MEMBRES__**\n"
    for x in c:
        pourcent = round(channels[x]['score']/allmsg*100, 2)
        if pourcent < 2:
            txt += "🟥 "
        elif pourcent < 10:
            txt += "🟨 "
        else:
            txt += "🟩 "
        txt += f"#{sc:2d} **{channels[x]['name']}** : **{pourcent}%** ({channels[x]['score']}) *{channels[x]['time']}ms*\n"
        csv += f"{channels[x]['name']}\t{channels[x]['score']}\n"
        sc += 1
    print(csv)
    txt += f"Temps écoulé : {round(time.time()-ttttime,1)}s"
    await ctx.send(txt)


@bot.command(name='clivage', help='')
async def clivage(ctx, *arr):
    global COOLDOWN
    if time.time() <= COOLDOWN+DUREE:
        await ctx.send(f"Veuillez attendre {round(COOLDOWN+DUREE-time.time())}s avant de recommencer :)")
        return
    COOLDOWN = time.time()
    bords = ["droite", "gauche"]
    gifs = ["https://imgur.com/6ovFm4w", "https://imgur.com/QTL952k"]
    if len(arr) > 0:
        l = " ".join(arr)
        num = randint(0, 1)
        if arr[0].lower() in ["les", "des", "mes", "ces"]:
            await ctx.send(f"{l} sont de {bords[num]}\n{gifs[num]}")
        elif arr[0].lower() in ["je", "j", "j'"]:
            await ctx.send(f"{l} suis de {bords[num]}\n{gifs[num]}")
        else:
            await ctx.send(f"{l} est de {bords[num]}\n{gifs[num]}")


@bot.command(name='test', help='')
async def test(ctx, jours=7, lim=1000):
    print("test")

# ----------------------------- FIN SETUP

# S'execute quand le bot est prêt; Affiche la liste des serveurs sur lesquelles le bot est actuellement


@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guild:')
    for guild in bot.guilds:
        print(f'-{guild.name}')
    print(f'{bot.user} has started')


def reponses_timbot(message):
    if "bot" in message.content.lower():
        if "merci" in message.content.lower():
            return "Mais de rien, "+str(message.author.display_name)+"!"
        if "bon" in message.content.lower():
            return ":3"
        if "nul" in message.content.lower() or "mauvais" in message.content.lower() or "merde" in message.content.lower():
            return ":'<"
        if "hein" in message.content.lower() and "?" in message.content.lower():
            if message.author.id == 123742890902945793:
                return "Mais oui, évidemment "+str(message.author.display_name)+"!"
            else:
                return "Pourquoi tu me demande? J'ai l'air d'être ton ami?"


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    msg = reponses_timbot(message)
    if msg is not None:
        await message.channel.send(msg)

    await bot.process_commands(message)


# lance le bot
bot.run(TOKEN)
