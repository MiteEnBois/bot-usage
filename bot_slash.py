from email import message
import os
import io
import discord
import time
import sys
import math
import re
import json
import difflib
import asyncio
from fuzzywuzzy.fuzz import ratio
import difflib
import requests
from random import randint
from datetime import datetime, timedelta
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord import Intents
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from w3lib.url import url_query_cleaner
from url_normalize import url_normalize
import copy

from fuzzywuzzy import process
# python -m pip install -r requirements.txt

# ----------------------------- SETUP VARIABLES GLOBALES ET BOT
print("start loading")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = Intents.default()
intents.reactions = True

intents.members = True

bot = commands.Bot(command_prefix=';', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

guild_ids = [444472133842894848, 147699691377655808, 370295251983663114]
# guild_ids = [370295251983663114, 147699691377655808]
q_cdza = {}
q_jdg = {}
q_wtc = {}
reaction_roles = {}

# with open("q_cdza.yml", encoding='utf-8') as f:
#     data = yaml.load(f, Loader=yaml.FullLoader)
#     if data is not None:
#         q_cdza = data
#     else:
#         q_cdza = {}
#     f.close()
#     print("q_cdza chargée")
# print(f"Temps écoulé : {round(time.time()-ttttime,1)}s")
# ttttime = time.time()

# with open("q_jdg.yml", encoding='utf-8') as f:
#     data = yaml.load(f, Loader=yaml.FullLoader)
#     if data is not None:
#         q_jdg = data
#     else:
#         q_jdg = {}
#     f.close()
#     print("q_jdg chargée")
# print(f"Temps écoulé : {round(time.time()-ttttime,1)}s")

with open("q_cdza.json", encoding='utf-8') as f:
    data = json.load(f)
    if data is not None:
        q_cdza = data
    else:
        q_cdza = {}
    f.close()
    print("q_cdza chargée")

with open("q_jdg.json", encoding='utf-8') as f:
    data = json.load(f)
    if data is not None:
        q_jdg = data
    else:
        q_jdg = {}
    f.close()
    print("q_jdg chargée")

with open("q_wtc.json", encoding='utf-8') as f:
    data = json.load(f)
    if data is not None:
        q_wtc = data
    else:
        q_wtc = {}
    f.close()
    print("q_wtc chargée")

with open("reaction_roles.json", encoding='utf-8') as f:
    data = json.load(f)
    if data is not None:
        reaction_roles = data
    else:
        reaction_roles = {}
    f.close()
    print("reaction_roles chargée")

# ----------------------------- FONCTIONS UTILITAIRES


@slash.slash(name="ping",
             description="Pings the bot",
             guild_ids=guild_ids)
async def ping(ctx):
    await ctx.send("Pong!!")


def clean_url(url):
    if "youtube.com" in url or "youtu.be" in url:
        return url
    # u = url_normalize(url)
    u = url
    u = url_query_cleaner(u, parameterlist=['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'], remove=True, keep_fragments=True)
    # if "cdn.discordapp.com" in u and ".gif" in u:
    #     u = u.replace("cdn.discordapp.com", "media.discordapp.net")

    if len(u) == len(url):
        u = url
    # headers = {'User-Agent': 'Mozilla/5.0'}
    # response = requests.get(u, headers=headers)
    # if response.history:
    #     u = response.url
    if "https://www.google.com/url?q=" in u:
        u = clean_url(u.replace("https://www.google.com/url?q=", ""))
    # ancre = re.search(r"\#\w*$", url)
    # if ancre is not None and ancre.group(0) not in u:
    #     u = u + ancre.group(0)
    if u[-1:] == '#':
        return u[:-1]
    else:
        return u


def clean_message(content):
    url_finder = re.compile(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
    finded = url_finder.findall(content)
    if finded == []:
        raise Exception("empty")
    if len(finded) >= 2:
        txt = "Liens propres : "
        verification = "Liens propres : "
    else:
        txt = "Lien propre : "
        verification = "Lien propre : "
    modifs = "Problèmes : "
    for t in finded:
        if t[-1:] == ">":
            t = t[:-1]
        u = clean_url(t)
        if "media.discordapp.net" in u:
            txt += u + "\n"

            verification += t + "\n"
        else:
            txt += "<" + u + ">\n"

            verification += "<" + t + ">\n"

        case_a = t
        case_b = u

        plus = ""
        moins = ""
        for li in difflib.ndiff(case_a, case_b):
            if li[0] != ' ':
                if li[0] == '+':
                    plus += li[2]
                else:
                    moins += li[2]
        modifs += moins

    if verification == txt:
        raise Exception("clean")
    else:
        if "media.discordapp.net" in txt:
            return txt
        return txt + modifs


def split_dict_to_multiple(input_dict, max_limit=2000):
    """Splits dict into multiple dicts with given maximum size. 
Returns a list of dictionaries."""

    chunks = []
    curr_dict = {}
    for k, v in input_dict.items():
        if len(curr_dict.keys()) < max_limit:
            curr_dict.update({k: v})
        else:
            chunks.append(copy.deepcopy(curr_dict))
            curr_dict = {k: v}
    # update last curr_dict
    chunks.append(curr_dict)
    return chunks


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
        content=f"{dict[t[used[reaction.emoji]]]['ep']}&t={dict[t[used[reaction.emoji]]]['time']}"
    )
    try:
        for x in used:
            await msg.clear_reaction(x)
    except:
        print("pas les bons role")


async def newquotes(ctx, phrase, source):
    titre = "Recherche en cours veuillez patienter"
    msg = await ctx.send(titre)
    if len(source) >= 5000:
        list_s = split_dict_to_multiple(source, round(len(source) / 10))
    else:
        list_s = [source]
    results = {}
    i = 1
    full = "█"
    empty = "░"
    for x in list_s:
        Ratios = process.extract(phrase, list(x))
        print(f"{i}/{len(list_s)}")
        if i % 2 == 0:
            await msg.edit(content=f"{titre}\n{full*i*2}{empty*((len(list_s)-i)*2)}")
        for r in Ratios:
            if r[1] < 87:
                break
            results[r[0]] = r[1]
        i += 1
    results = list(dict(sorted(results.items(), key=lambda item: item[1], reverse=True)))
    print(results)
    answer = ""
    if len(results) != 1:
        txt = "**__LISTE DES QUOTES TROUVEE__**\n"
        emoji = [
            "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
        ]

        used = {}
        i = 0
        for x in results:
            txt += f"{emoji[i]} {x} -> {source[x]['title']}, à {source[x]['time']}s\n"  # ({dict[x]['ep']}&t={dict[x]['time']})
            used[emoji[i]] = i
            i += 1
        await msg.edit(content=f"{txt}")
        for x in used:
            await msg.add_reaction(x)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in used

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=40, check=check)
        except asyncio.TimeoutError:
            await msg.edit(content=f"Temps écoulé pour \"{phrase}\"")
            try:
                for x in used:
                    await msg.clear_reaction(x)
            except:
                print("pas les bons role")
            return
        answer = results[used[reaction.emoji]]
    else:
        answer = results[0]
    await msg.edit(
        content=f"{source[answer]['ep']}&t={source[answer]['time']}"
    )
    try:
        for x in used:
            await msg.clear_reaction(x)
    except:
        print("pas les bons role")


@slash.slash(name="cdza",
             description="Recherche une quote de cdza et affiche celles qui sont proche de la phrase entrée",
             options=[
                 create_option(
                     name="phrase",
                     description="Notez la quote que vous recherchez",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def cdza(ctx, phrase):
    await quotes(ctx, phrase.lower(), q_cdza)


@slash.slash(name="jdg",
             description="Recherche une quote de jdg et affiche celles qui sont proche de la phrase entrée",
             options=[
                 create_option(
                     name="phrase",
                     description="Notez la quote que vous recherchez",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def jdg(ctx, phrase):
    await quotes(ctx, phrase.lower(), q_jdg)


@slash.slash(name="testjdg",
             description="Ne marche pas a priori",  # "Recherche une quote de jdg et affiche celles qui sont proche de la phrase entrée",
             options=[
                 create_option(
                     name="phrase",
                     description="Notez la quote que vous recherchez",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def testjdg(ctx, phrase):
    await newquotes(ctx, phrase.lower(), q_jdg)


@slash.slash(name="wtc",
             description="Recherche une quote de wtc et affiche celles qui sont proche de la phrase entrée",
             options=[
                 create_option(
                     name="phrase",
                     description="Notez la quote que vous recherchez",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def wtc(ctx, phrase):
    await quotes(ctx, phrase.lower(), q_wtc)


@slash.slash(name="boule",
             description="Secoue la boule magique et obtient les réponse à tes questions",
             options=[
                 create_option(
                     name="question",
                     description="Notez la quote que vous recherchez",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def boule(ctx, question):
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

    str = question
    for x in rempl:
        # str = str.replace(x, rempl[x])
        # sub = f"\b{x}\b"
        str = re.subn(rf"\b{x}\b", rempl[x], str)[0]
    if str[-1] != '?':
        if str[-1] != ' ':
            str += ' '
        str += '?'
    await ctx.send(f"{str.capitalize()} : 🎱**{boule[randint(0, 19)]}**🎱")


@slash.slash(name="clear",
             description="supprimes les messages d\'un canal. Le canal doit avoir '_' comme 1er charactère",
             options=[
                 create_option(
                     name="jours",
                     description="L'age minimum des messages à supprimer, en jours; 0 pour tout les messages",
                     option_type=4,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def clear(ctx, jours):
    channel = ctx.channel
    datef = datetime.fromtimestamp(time.time()) - timedelta(days=jours)
    if channel.name[0] != "_":
        await ctx.send("Commande clear interdite ici", delete_after=10)
        return

    await ctx.defer()
    messages = len(await channel.history(limit=10000, before=datef).flatten())
    if messages == 0 or messages is None:
        await ctx.send("Pas de messages à supprimer", delete_after=10)
        return
    conf = await ctx.send(f"Vous êtes sur le point de supprimer {messages} messages, souhaitez vous continuer? Envoyez Oui pour confirmer", delete_after=40)

    def check(m):
        return m.content == "Oui" and m.channel == channel and m.author == ctx.author

    try:
        resp = await bot.wait_for("message", check=check, timeout=30)
        print(f"deleting {messages} messages")
        # await conf.delete()
        await resp.delete()
        # await ctx.message.delete()
        await channel.purge(limit=10000, before=datef)

    except asyncio.TimeoutError:
        await conf.edit(content="Timeout")
        await asyncio.sleep(10)
        # await conf.delete()
        # await ctx.message.delete()


@slash.slash(name="usage",
             description="Compte les messages de chaque canal afin de comparer leur utilité",
             options=[
                 create_option(
                     name="jours",
                     description="Age maximum des messages à compter",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="limite",
                     description="Nombre maximum de message à compter par canal",
                     option_type=4,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def usage(ctx, jours, limite):
    datef = datetime.fromtimestamp(time.time()) - timedelta(days=jours)
    ttttime = time.time()
    channels = {}
    full = "█"
    empty = "░"
    if limite == 0:
        limite = None
    list_channels = []
    for c in ctx.guild.channels:

        if c.type == discord.ChannelType.text:
            if c.members != []:
                list_channels.append(c)

    chan_count = len(list_channels)

    msg = await ctx.send(f"Comptage en cours veuillez patienter\n{0:2d}/{chan_count:2d} {empty*20} 0%")
    print(f"chan count : {chan_count}")
    chan_processed = 0
    percent = 0
    allmsg = 0
    for chan in list_channels:
        try:
            if (str(chan.type) != "text"):  # chan.name[0] == "_" or
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
                async for message in chan.history(limit=limite):
                    if message.author.bot:
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
            print("forbidden channel")
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
                content=f"Comptage en cours veuillez patienter\n{chan_processed:2d}/{chan_count:2d} {full*percent}{empty*(20-percent)} {math.floor(chan_processed / chan_count * 100)}%"
            )
    print("---------------------------")
    await msg.edit(content=f"{msg.content}\nGénération du graphique en cours, veuillez patienter ...")
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
        t = ""
        if pourcent < 0.5:
            t += "🟥 "  #
        elif pourcent < 2:
            t += "🟧 "
        elif pourcent < 10:
            t += "🟨 "
        else:
            t += "🟩 "
        t += f"#{sc:2d} **{channels[x]['name']}** : **{pourcent}%** ({channels[x]['score']}) *{channels[x]['time']}ms*\n"
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
        if len(value['name']) >= 2 and value['name'][1] == "-":
            value['name'] = value['name'][2:]
        if len(value['name']) >= 3 and value['name'][2] == "-":
            value['name'] = value['name'][3:]
    data = channels
    stats = sorted([(value['score'], f"{value['name']}")
                    for key, value in data.items()])

    labels = [value for key, value in stats]
    values = [key for key, value in stats]
    fig, ax = plt.subplots()
    plt.barh(labels, values, color="#ffdc54")

    size = chan_count / 3

    fig.set_figheight(size)
    fig.set_figwidth(10)

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


@slash.slash(name="clivage",
             description="Dit si quelque chose est de gauche ou de droite",
             options=[
                 create_option(
                     name="phrase",
                     description="Notez la chose que vous voulez clivager",
                     option_type=3,
                     required=True
                 )
             ], guild_ids=guild_ids)
async def clivage(ctx, phrase):
    bords = ["drouate", "gôche"]
    gifs = ["https://imgur.com/6ovFm4w", "https://imgur.com/QTL952k"]
    if len(phrase) > 0:
        l = phrase
        num = randint(0, 1)
        if phrase.split(" ")[0].lower() in ["les", "des", "mes", "ces"]:
            await ctx.send(f"{l} sont de {bords[num]}\n{gifs[num]}")
        else:
            await ctx.send(f"{l} est de {bords[num]}\n{gifs[num]}")


@bot.command(name='test', help='')
async def test(ctx):
    print(ctx)


def check_role(ctx, rolestr):
    pure_id = re.search("^(\d{18})$", rolestr)
    from_mention = re.search("^<@&(\d{18})>$", rolestr)
    roleid = 0
    if pure_id:
        roleid = int(pure_id.group(1))
    elif from_mention:
        roleid = int(from_mention.group(1))
    if roleid == 0:
        return None
    return ctx.guild.get_role(roleid)


@slash.slash(name="creerreactionrole",
             description="Créé un message de reaction",
             options=[
                 create_option(
                     name="message",
                     description="L'id du message qu'il faut lier",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="role",
                     description="Le role que vous voulez rajouter",
                     option_type=3,
                     required=True
                 )
             ],
             guild_ids=guild_ids)
async def creerreactionrole(ctx, message, role):
    r = check_role(ctx, role)
    if not r:
        await ctx.send("Role incorrect")
        return
    reaction_roles[message] = r.id
    await ctx.send("Message lié!")
    with open('reaction_roles.json', 'w+', encoding='utf-8') as outfile:
        outfile.truncate(0)
        json.dump(reaction_roles, outfile, indent=4)
    return


@slash.slash(name="changerreactionrole",
             description="Change le role lié à un message",
             options=[
                 create_option(
                     name="message",
                     description="L'id du message qu'il faut lier",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="role",
                     description="Le nouveau role que vous voulez rajouter",
                     option_type=3,
                     required=True
                 )
             ],
             guild_ids=guild_ids)
async def changerreactionrole(ctx, message, role):
    r = check_role(ctx, role)
    if not r:
        await ctx.send("Role incorrect")
        return
    reaction_roles[message] = r.id
    await ctx.send("Role changé!")
    with open('reaction_roles.json', 'w+', encoding='utf-8') as outfile:
        outfile.truncate(0)
        json.dump(reaction_roles, outfile, indent=4)
    return


@slash.slash(name="supprimerreactionrole",
             description="Supprime un message de reaction",
             options=[
                 create_option(
                     name="message",
                     description="L'id du message qu'il faut lier",
                     option_type=3,
                     required=True
                 )
             ],
             guild_ids=guild_ids)
async def supprimerreactionrole(ctx, message):
    reaction_roles.pop(message)
    await ctx.send("Lien supprimé!")
    with open('reaction_roles.json', 'w+', encoding='utf-8') as outfile:
        outfile.truncate(0)
        json.dump(reaction_roles, outfile, indent=4)
    return
# ----------------------------- FIN SETUP

# S'execute quand le bot est prêt; Affiche la liste des serveurs sur lesquelles le bot est actuellement


@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.message_id) in reaction_roles:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(int(reaction_roles[str(payload.message_id)]))
        await payload.member.add_roles(role)
    return


@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.message_id) in reaction_roles:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(int(reaction_roles[str(payload.message_id)]))
        await member.remove_roles(role)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(f"with slash commands"))
    print(f'{bot.user} is connected to the following guild:')
    for guild in bot.guilds:
        print(f'-{guild.name}')
    print(f'{bot.user} has started')
    await bot.get_guild(int(os.getenv('ERROR_GUILD'))).get_channel(int(os.getenv('ERROR_CHANNEL'))).send("Bot Loaded")


@bot.event
async def on_command_error(ctx, error):
    await bot.get_guild(int(os.getenv('ERROR_GUILD'))).get_channel(int(os.getenv('ERROR_CHANNEL'))).send(error)

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

ignored = [147700545006600192]


@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.id in ignored:
        return
    try:
        clean = clean_message(message.content)
    except Exception as ex:
        # reason = ex.args[0]
        # if reason == "empty":
        #     nothing = 0
        # if reason == "clean":
        # await message.add_reaction("👍")

        await bot.process_commands(message)
        return
    await message.channel.send(clean)
    # await message.add_reaction("👎")
    await bot.process_commands(message)
    # msg = reponses_timbot(message)
    # if msg is not None:
    #     await message.channel.send(msg)

# lance le bot
bot.run(TOKEN)
