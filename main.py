import os
import discord
import tempfile
import aiohttp
import asyncio
import random
import wc
import wordcloud
import xml.etree.ElementTree as ET
from aiohttp_socks import ProxyConnector
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

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
    url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags=-rating:safe"
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            result = await response.read()
            tree = ET.fromstring(result.decode('utf-8'))
            post = random.choice(tree)
            message = await ctx.send(f"{post.find('sample_url').text}")
            await asyncio.sleep(60)
            await ctx.message.delete()
            await message.delete()


@bot.command(name="poke")
async def poke(ctx, *targets):
    for target in targets:
        await ctx.send(f"{target} hey, wake up!")


@bot.command(name="words")
async def words(ctx: commands.Context, n="200"):
    messages = await ctx.channel.history(limit=int(n)).flatten()
    words = wc.cloud((m.content for m in messages), ctx.guild)
    cloud = wordcloud.WordCloud(
        width=1960, height=1080).generate_from_frequencies(words).to_image()
    image = BytesIO()
    cloud.save(image, format="PNG")
    image.seek(0)
    await ctx.channel.send(file=discord.File(
        fp=image, filename="word_cloud.png"))


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
    else:
        await ctx.message.reply("Зайди в войс, фашист!")

bot.run(token)
