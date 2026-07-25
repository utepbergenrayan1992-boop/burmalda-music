import os
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354
YANDEX_DISK_URL = "https://disk.yandex.kz/d/pchRD7P7IxItMg"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_direct_stream_url():
    """Получает прямую ссылку, маскируясь под реальный браузер"""
    base_url = "https://yandex.net"
    
    # Заголовки, которые заставят Яндекс поверить, что это человек из Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(
            base_url, 
            params={'public_key': YANDEX_DISK_URL}, 
            headers=headers, 
            timeout=15
        )
        if response.status_code == 200:
            return response.json().get('href')
        
        # Если API выдал ошибку, пробуем получить прямую веб-ссылку в лоб
        print(f"Яндекс API заблокировал запрос ({response.status_code}). Пробуем обходной путь...", flush=True)
        html_res = requests.get(YANDEX_DISK_URL, headers=headers, timeout=15)
        if "file" in html_res.text:
             print("Найден обходной веб-интерфейс, запрашиваем повторно...", flush=True)
             
    except Exception as e:
        print(f"Ошибка сети Яндекс API: {e}", flush=True)
    return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запрашиваем ссылку у Яндекса...", flush=True)
        loop = asyncio.get_event_loop()
        stream_url = await loop.run_in_executor(None, get_direct_stream_url)

        if not stream_url:
            print("Яндекс не отдал ссылку из-за капчи. Ждем 20 секунд и пробуем снова...", flush=True)
            await asyncio.sleep(20)
            continue

        print("Яндекс одобрил запрос! Запуск онлайн-трансляции трека...", flush=True)
        source = None
        try:
            source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            vc.play(source)
        except Exception as e:
            print(f"Сбой FFmpeg при воспроизведении: {e}", flush=True)
            await asyncio.sleep(10)
            continue

        while vc.is_connected() and vc.is_playing():
            await asyncio.sleep(2)

        if source:
            try: source.cleanup()
            except Exception: pass
        await asyncio.sleep(2)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен на Railway 24/7!", flush=True)
    
    try:
        if not discord.opus.is_loaded():
            discord.opus.load_opus()
    except Exception:
        pass

    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Не удалось подключиться к каналу: {e}", flush=True)

bot.run(TOKEN)
