import os
import discord
import tempfile
import aiohttp
import random
import xml.etree.ElementTree as ET
from aiohttp_socks import ProxyConnector
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="$")
emojis = None


@bot.event
async def on_ready():
    global emojis
    if not emojis:
        emojis = {e.name: str(e) for e in bot.emojis}
    print(f"{bot.user} has connected to Discord")
    for guild in bot.guilds:
        print(f"Connected to guild {guild.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if ":boop:" in message.content:
        await message.reply(content="ФАШИСТ")
    else:
        await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    if type(reaction.emoji) is not str and reaction.emoji.name == "boop":
        await reaction.message.channel.send(f"{user.mention} ФАШИСТ")


@bot.command(name="hentai")
async def hentai(ctx, arg=None):
    connector = ProxyConnector.from_url(
        'socks5://127.0.0.1:1080')
    url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags=rating:explicit"
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            result = await response.read()
            tree = ET.fromstring(result.decode('ascii'))
            post = random.choice(tree)
            await ctx.send(f"{post.find('sample_url').text}")


@bot.command(name="poke")
async def poke(ctx, *targets):
    for target in targets:
        await ctx.send(f"{target} hey, wake up!")


@bot.command(name="boop")
async def boop(ctx, *targets):
    global emojis
    for target in targets:
        await ctx.send(f"{emojis['boop']} {target} УЙМИСЬ ФАШИСТ")


@bot.command(name="say")
async def say(ctx: commands.Context, lang, *msg):
    if ctx.author.voice:
        msg = " ".join(msg)
        tts = gTTS(msg, lang=lang)

        with tempfile.NamedTemporaryFile(mode='wb') as file:
            tts.write_to_fp(file)
            channel = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            if channel:
                channel.move_to(ctx.author.voice.channel)
            else:
                channel = await ctx.author.voice.channel.connect()
            stream = await discord.FFmpegOpusAudio.from_probe(file.name)
            channel.play(stream)
            while channel.is_playing():
                pass
            await channel.disconnect()

bot.run(token)
