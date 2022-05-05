import asyncio
from urllib import response
import discord
from discord.ext import commands, tasks
import youtube_dl
from random import choice
from discord.voice_client import VoiceClient


youtube_dl.utils.bug_reports_message=lambda:''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses causes issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YoutubeDlSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *,data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop = None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options),data = data)
        

client = commands.Bot(command_prefix ='?')
status = ['Cristiano is The Best player in the world','SIUU', 'Sleeping!']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.command(name = 'ping', help='This command return the latency')
async def ping(ctx):
    await ctx.send(f'**SIUU!** Speed: {round(client.latency * 1000)}ms')

@client.command(name = 'hello', help = 'Return random welcome message')
async def hello(ctx):
    response = ['***Fuck!*** Why did you wake me up?', 'Hello, SIUU!', 'Can i help you?' ,'Im better than Messi']
    await ctx.send(choice(response))

@client.command(name = 'kill', help='Return bot last words')
async def kill(ctx):
    response = ['**SHit** You just kill me','why did you kill me?' ,'i have family too bitch?!']
    await ctx.send(choice(response))

@client.command(name = 'credit', help='Return credit')
async def credit(ctx):
    await ctx.send('Author: Tien Cong Nguyen -**Ronaldofanboy**')
    await ctx.send('Thanks for using this bot! Hope you use it well')
    await ctx.send('Send me email if you want to use this bot source code: nc762857@gmail.com')

@client.command(name = 'play', help='This command play music')
async def play(ctx,url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to the server")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YoutubeDlSource.from_url(url,  loop = client.loop)
        voice_channel.play(player, after = lambda e: print('Player error: %s % e') if e else None)

    await ctx.send('**Playing:** {}'.format(player.title))

@client.command(name='stop', help = 'This command stops the musics and make the bot leave the channel ')
async def stop(ctx):
    voice_client = ctx.message.guild.voice.client
    await voice_client.disconnect()



@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


client.run('Enter Your Token Here')

