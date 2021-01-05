import os, io
import discord
import time
import sys
import math
import re
import yaml
import difflib
import asyncio
from lxml import html
import requests
from random import shuffle, randint, seed
from datetime import datetime, timedelta, date
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import matplotlib.pyplot as plt
#python -m pip -r install requirements.txt

# ----------------------------- SETUP VARIABLES GLOBALES ET BOT
print("start loading")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PASSWORD = os.getenv('PASSWORD')

bot = commands.Bot(command_prefix=';')

ttttime = time.time()
q_cdza = {}

with open("q_cdza.yml", encoding='utf-8') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    if data is not None:
        q_cdza = data
    else:
        q_cdza = {}
    f.close()
    print("q_cdza chargée")
print(f"Temps écoulé : {round(time.time()-ttttime,1)}s")
# ttttime = time.time()
# q_jdg = {}

# with open("q_jdg.yml", encoding='utf-8') as f:
#     data = yaml.load(f, Loader=yaml.FullLoader)
#     if data is not None:
#         q_jdg = data
#     else:
#         q_jdg = {}
#     f.close()
#     print("q_jdg chargée")
# print(f"Temps écoulé : {round(time.time()-ttttime,1)}s")

page = requests.get(
    'https://en.wikipedia.org/wiki/List_of_The_Expanse_episodes')
tree = html.fromstring(page.content)

tx = tree.xpath("//tr[@class = 'vevent']/td[@class = 'summary']/text()")
ta = tree.xpath("//tr[@class = 'vevent']/td[@class = 'summary']/a/text()")
titlesExpanse = []

for a in ta:
    titlesExpanse.append(f"\"{a}\"")
for x in tx:
    if x != '"':
        titlesExpanse.append(x)

desc = tree.xpath("//tr[@class = 'expand-child']/td[@class = 'description']")
descriptionExpanse = []

for x in desc:
    nodes = x.xpath("./node()")
    txt = ""
    for n in nodes:
        try:
            txt += f'*{n.xpath("./text()")[0]}*'
        except:
            txt += f'{n}'
    descriptionExpanse.append(txt.replace("\n", ""))

print("Trucs expanse chargés")

# ----------------------------- FONCTIONS UTILITAIRES


@bot.command(name='ping', help='Pong!')
async def ping(ctx):
    await ctx.send("Pong!")


# ----------------------------- COMMANDES


async def quotes(ctx, phrase, dict):
    msg = await ctx.send("Recherche en cours veuillez patienter")
    t = []
    num = 0.8
    while len(t) < 2 or num == 0:
        num -= 0.05
        t = difflib.get_close_matches(phrase, dict, n=10, cutoff=num)
    txt = "**__LISTE DES QUOTES TROUVEE__**\n"
    emoji = [
        "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
    ]

    used = {}
    i = 0
    for x in t:
        txt += f"{emoji[i]} {x} -> {dict[x]['title']}, à {dict[x]['time']}s\n"  # ({dict[x]['ep']}&t={dict[x]['time']})
        used[emoji[i]] = i
        i += 1
    await msg.edit(content=f"{txt}")
    for x in used:
        await msg.add_reaction(x)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in used

    try:
        reaction, user = await bot.wait_for('reaction_add',
                                            timeout=40,
                                            check=check)
    except asyncio.TimeoutError:
        await msg.edit(content=f"Temps écoulé pour \"{phrase}\"")
        try:
            for x in used:
                await msg.clear_reaction(x)
        except:
            print("pas les bons role")
        return
    await msg.edit(
        content=
        f"{dict[t[used[reaction.emoji]]]['ep']}&t={dict[t[used[reaction.emoji]]]['time']}"
    )
    try:
        for x in used:
            await msg.clear_reaction(x)
    except:
        print("pas les bons role")


@bot.command(
    name='cdza',
    help=
    'Recherche une quote de cdza et affiche celles qui sont proche de la phrase entrée. Attention, la phrase donnée doit etre précise pour trouver votre quote'
)
async def cdza(ctx, *arr):
    await quotes(ctx, ' '.join(arr).lower(), q_cdza)


# @bot.command(
#     name='jdg',
#     help=
#     'Recherche une quote de jdg et affiche celles qui sont proche de la phrase entrée. Attention, la phrase donnée doit etre précise pour trouver votre quote'
# )
# async def jdg(ctx, *arr):
#     await quotes(ctx, ' '.join(arr).lower(), q_jdg)


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
    boule = [
        "Essaye plus tard", "Essaye encore", "Pas d'avis", "C'est ton destin",
        "Le sort en est jeté", "Une chance sur deux", "Repose ta question",
        "D'après moi oui", "C'est certain", "Oui absolument",
        "Tu peux compter dessus", "Sans aucun doute", "Très probable", "Oui",
        "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver",
        "N'y compte pas", "Impossible"
    ]
    rempl = {
        "mon": "ton",
        "me": "te",
        "ma": "ta",
        "mes": "tes",
        "j": "t",
        "je": "tu",
        "suis": "es",
        "ai": "a"
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


@bot.command(
    name='clear',
    help=
    'supprimes les messages d\'un canal. jours=a partir de quand ca delete\nPar défaut supprime les messages plus vieux qu\'un jour; 0 pour tout les messages'
)
async def clear(ctx, jours=1):
    datef = datetime.fromtimestamp(time.time()) - timedelta(days=jours)
    if ctx.channel.name[0] != "_":
        m = await ctx.send("Commande interdite ici")
        await asyncio.sleep(10)
        await m.delete()
        await ctx.message.delete()
        return
    messages = len(await ctx.channel.history(limit=1000,
                                             before=datef).flatten())
    if messages == 0 or messages is None:
        m = await ctx.send("Pas de messages à supprimer")
        await asyncio.sleep(10)
        await m.delete()
        await ctx.message.delete()
        return
    conf = await ctx.send(
        f"Vous êtes sur le point de supprimer {messages} messages, souhaitez vous continuer? Envoyez Oui pour confirmer"
    )

    def check(m):
        return m.content == "Oui" and m.channel == ctx.channel and m.author == ctx.author

    try:
        resp = await bot.wait_for("message", check=check, timeout=30)
        print("deleting")
        await conf.delete()
        await resp.delete()
        await ctx.message.delete()
        await ctx.channel.purge(limit=1000, before=datef)

    except asyncio.TimeoutError:
        await conf.edit(content="Timeout")
        await asyncio.sleep(10)
        await conf.delete()
        await ctx.message.delete()


@bot.command(
    name='usage',
    help=
    'compte les messages de chaque canal dans les x derniers jours. usage: ;usage <jours(defaut 7)> <limite message(defaut 500)>'
)
async def usage(ctx, jours=7, lim=1000, all_chan=False):
    datef = datetime.fromtimestamp(time.time()) - timedelta(days=jours)
    ttttime = time.time()
    channels = {}
    categories = [
        756867463916027976, 757612262054821949, 360597432758829056,
        777349957765693460
    ]
    full = "█"
    empty = "░"

    chan_count = 0
    if all_chan:
        for x in ctx.guild.channels:
            if (str(x.type) == "text" and x.name[0] != "_"):
                try:
                    await x.history(limit=1).flatten()
                except discord.errors.Forbidden:
                    print("forbiden channel")
                    continue
                chan_count += 1
    else:
        for x in ctx.guild.categories:
            if x.id in categories:
                chan_count += len(x.channels)
    msg = await ctx.send(
        f"Comptage en cours veuillez patienter\n{0:2d}/{chan_count:2d} {empty*20} 0%"
    )
    print(f"chan count : {chan_count}")
    chan_processed = 0
    percent = 0
    allmsg = 0
    for chan in ctx.guild.channels:
        if not all_chan and (chan.category is None
                             or chan.category.id not in categories):
            continue
        try:
            if chan.name[0] == "_" or (str(chan.type) != "text"):
                continue
            if (str(chan.type) == "text"):
                channels[int(chan.id)] = {
                    "name": chan.name,
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
                delta = round((time.time() - temptime) * 1000.0)
                channels[chan.id]["time"] = delta
                print(f"{chan};{i};{delta}")
                allmsg += i
        except discord.errors.Forbidden:
            print("forbiden channel")
            channels.pop(int(chan.id))
        except:
            print("Unexpected error:", sys.exc_info())
            for x in sys.exc_info():
                print(x)
            continue
        chan_processed += 1
        if math.floor(chan_processed / chan_count * 20) > percent:
            percent = math.floor(chan_processed / chan_count * 20)
            await msg.edit(
                content=
                f"Comptage en cours veuillez patienter\n{chan_processed:2d}/{chan_count:2d} {full*percent}{empty*(20-percent)} {math.floor(chan_processed / chan_count * 100)}%"
            )
    print("---------------------------")
    sc = 1
    c = {
        k: v
        for k, v in sorted(
            channels.items(), key=lambda item: item[1]["score"], reverse=True)
    }
    # with open('data_test.json', 'w') as outfile:
    #     json.dump(channels, outfile)

    new_message = False
    txt = f'**__UTILISATION DES CANAUX DU SERVEUR "{ctx.guild.name.upper()}" DANS LES {jours} DERNIERS JOURS__**\n'
    for x in c:
        pourcent = round(channels[x]['score'] / allmsg * 100, 2)
        if pourcent < 0.5:
            txt += "🟥 "  #
        elif pourcent < 2:
            txt += "🟧 "
        elif pourcent < 10:
            txt += "🟨 "
        else:
            txt += "🟩 "
        t = f"#{sc:2d} **{channels[x]['name']}** : **{pourcent}%** ({channels[x]['score']}) *{channels[x]['time']}ms*\n"
        if (len(txt) + len(t)) >= 2000:
            if new_message:
                await ctx.send(txt)
            else:
                await msg.edit(content=txt)
                new_message = True
            txt = ""
        txt += t
        sc += 1
    txt += f"Nombre total de messages : {allmsg}\n"

    for key, value in channels.items():
        if value['name'][1] == "-":
            value['name'] = value['name'][2:]
    data = channels
    stats = sorted([(value['score'], f"{value['name']}")
                    for key, value in data.items()])

    labels = [value for key, value in stats]
    values = [key for key, value in stats]
    fig, ax = plt.subplots()
    plt.barh(labels, values, color="#ffdc54")

    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)

    plt.ylabel('Canaux')
    plt.xlabel('Nombre de message')
    plt.title(
        f'Utilisation des canaux du serveur "{ctx.guild.name}" dans les {jours} derniers jours'
    )
    # plt.box(on=None)

    for index, value in enumerate(values):
        plt.text(x=value + 10,
                 y=index - 0.25,
                 s=f"{value}, {round(value/sum(values)*100, 2)}%")

    fig = io.BytesIO()

    plt.savefig(fig, bbox_inches='tight', format="png")
    fig.seek(0)

    txt += f"Temps écoulé : {round(time.time()-ttttime,1)}s"
    if new_message:
        await ctx.send(txt)
    else:
        await msg.edit(content=txt)
    await ctx.send(file=discord.File(fig, 'usage.png'))


@bot.command(name='clivage', help='donne droite ou gauche de maniere random')
async def clivage(ctx, *arr):
    bords = ["drouate", "gôche"]
    gifs = ["https://imgur.com/6ovFm4w", "https://imgur.com/QTL952k"]
    if len(arr) > 0:
        l = " ".join(arr)
        num = randint(0, 1)
        if arr[0].lower() in ["les", "des", "mes", "ces"]:
            await ctx.send(f"{l} sont de {bords[num]}\n{gifs[num]}")
        else:
            await ctx.send(f"{l} est de {bords[num]}\n{gifs[num]}")


@bot.command(name='test', help='')
async def test(ctx):
    print(ctx)


@bot.command(name='expanse', help='')
async def expanse(ctx, desc=False, n=-1):
    eps = [10, 13, 13, 10]
    start = date(2020, 10, 31)
    num = (date.today() - start).days
    if n != -1:
        num = n
    if num < 0:
        await ctx.send("Patience, il faut encore attendre un peu")
        return
    if num >= 46:
        await ctx.send(
            "**LISTE DES DATES DE SORTIE : **\nS05E01 : **\"Exodus\"**; sortie : December 16, 2020\nS05E02 : **\"Churn\"**; sortie : December 16, 2020\nS05E03 : **\"Mother\"**; sortie : December 16, 2020\nS05E04 : **\"Guagamela\"**; sortie : December 23, 2020\nS05E05 : **\"Down and Out\"**; sortie : December 30, 2020\nS05E06 : **\"Tribes\"**; sortie : January 6, 2021\nS05E07 : **\"Oyedeng\"**; sortie : January 13, 2021\nS05E08 : **\"Hard Vacuum\"**; sortie : January 20, 2021\nS05E09 : **\"Winnipesaukee\"**; sortie : January 27, 2021\nS05E10 : **\"Nemesis Games\"**; sortie : February 3, 2021\n"
        )
        return

    s = 1
    ep = num
    for i in range(len(eps)):
        if num + 1 > eps[i]:
            s = i + 2
            num -= eps[i]
        else:
            break
    if s < 5 and desc:
        await ctx.send(
            f"Episode d'aujourd'hui : **S{s:02}E{num+1:02} : {titlesExpanse[ep]}** \n||{descriptionExpanse[ep]}||"
        )
    else:
        await ctx.send(
            f"Episode d'aujourd'hui : **S{s:02}E{num+1:02} : {titlesExpanse[ep]}**"
        )


# ----------------------------- FIN SETUP

# S'execute quand le bot est prêt; Affiche la liste des serveurs sur lesquelles le bot est actuellement


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(f"{bot.command_prefix}help"))
    print(f'{bot.user} is connected to the following guild:')
    for guild in bot.guilds:
        print(f'-{guild.name}')
    print(f'{bot.user} has started')


# def reponses_timbot(message):
#     if "bot" in message.content.lower():
#         if "merci" in message.content.lower():
#             return "Mais de rien, " + str(message.author.display_name) + "!"
#         if "bon" in message.content.lower():
#             return ":3"
#         if "nul" in message.content.lower(
#         ) or "mauvais" in message.content.lower(
#         ) or "merde" in message.content.lower():
#             return ":'<"
#         if "hein" in message.content.lower() and "?" in message.content.lower(
#         ):
#             if message.author.id == 123742890902945793:
#                 return "Mais oui, évidemment " + str(
#                     message.author.display_name) + "!"
#             else:
#                 return "Pourquoi tu me demande? J'ai l'air d'être ton ami?"


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # msg = reponses_timbot(message)
    # if msg is not None:
    #     await message.channel.send(msg)

    await bot.process_commands(message)


# lance le bot
bot.run(TOKEN)
