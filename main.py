import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530510035321356338
YOUTUBE_URL = "https://www.youtube.com/watch?v=s33REwDxvqc&list=RDs33REwDxvqc&start_radio=1&pp=ygUV0LHRg9GA0LzQsNC70LTQsCDRhNC8oAcB"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def setup_cookies():
    cookie_raw_text = os.getenv("YT_COOKIES_BASE64")
    if cookie_raw_text:
        try:
            with open("temp_cookies.txt", "w", encoding="utf-8") as f:
                f.write(cookie_raw_text)
            return "temp_cookies.txt"
        except Exception as e:
            print(f"Ошибка сохранения куков: {e}", flush=True)
    return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запуск безопасного стриминга YouTube с куками...", flush=True)
        cookie_file = setup_cookies()
        source = None
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'bestaudio/best', 
                'noplaylist': True,
                'extractor_args': {'youtube': {'player_client': ['web_embedded', 'web', 'tv']}}
            }
            
            if cookie_file:
                ydl_opts['cookiefile'] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(YOUTUBE_URL, download=False)
                stream_url = info['url']
                
            source = discord.FFmpegPCMAudio(
                stream_url, 
                before_options=FFMPEG_OPTIONS['before_options'], 
                options=FFMPEG_OPTIONS['options']
            )
            vc.play(source)
        except Exception as e:
            print(f"Ошибка стриминга: {e}", flush=True)
            if source:
                source.cleanup()
            await asyncio.sleep(5)
            continue
        finally:
            if cookie_file and os.path.exists(cookie_file):
                try:
                    os.remove(cookie_file)
                except Exception:
                    pass

        while vc.is_connected() and vc.is_playing():
            await asyncio.sleep(2)
        
        if source:
            try:
                source.cleanup()
            except Exception:
                pass
                
        print("Поток завершен. Перезапуск цикла...", flush=True)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен в режиме безопасного обхода блокировок!", flush=True)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception:
            pass

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        await asyncio.sleep(5)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
                bot.loop.create_task(play_playlist(vc))
            except Exception:
                pass

bot.run(TOKEN)
