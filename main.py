import os
import asyncio
import base64
import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530510035321356338
YOUTUBE_URL = "https://www.youtube.com/watch?v=5h84DVeMom4"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Безопасное создание временного файла с куками из переменной окружения
def setup_cookies():
    cookie_base64 = os.getenv("YT_COOKIES_BASE64")
    if cookie_base64:
        try:
            cookie_data = base64.b64decode(cookie_base64)
            with open("temp_cookies.txt", "wb") as f:
                f.write(cookie_data)
            return "temp_cookies.txt"
        except Exception as e:
            print(f"Ошибка декодирования куков: {e}", flush=True)
    return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запуск безопасного стриминга YouTube с куками...", flush=True)
        
        # Создаем временный файл перед запуском трека
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
            # Сразу удаляем файл куков с диска для полной безопасности
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
