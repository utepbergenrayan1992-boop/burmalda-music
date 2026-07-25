import os
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354

# Твоя точная публичная ссылка на файл
YANDEX_DISK_URL = "https://disk.yandex.kz/d/pchRD7P7IxItMg"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_yandex_direct_url(public_url):
    # Используем строго официальное API без ручных склеек доменов
    api_url = "https://yandex.net"
    try:
        response = requests.get(api_url, params={'public_key': public_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get('href')
        print(f"API Яндекса вернул ошибку {response.status_code}: {response.text}", flush=True)
        return None
    except Exception as e:
        print(f"Ошибка запроса к API Яндекса: {e}", flush=True)
        return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запрашиваем прямую ссылку у API Яндекса...", flush=True)
        stream_url = get_yandex_direct_url(YANDEX_DISK_URL)
        
        if not stream_url:
            print("Ошибка получения ссылки. Ждем 10 сек...", flush=True)
            await asyncio.sleep(10)
            continue

        print("Запуск бесконечного стриминга трека BURMALDA FM...", flush=True)
        source = None
        try:
            source = discord.FFmpegPCMAudio(
                stream_url, 
                before_options=FFMPEG_OPTIONS['before_options'], 
                options=FFMPEG_OPTIONS['options']
            )
            vc.play(source)
        except Exception as e:
            print(f"Ошибка при запуске FFmpeg: {e}", flush=True)
            if source:
                source.cleanup()
            await asyncio.sleep(5)
            continue

        # Бесшовный перезапуск каждые 10 минут, чтобы поток не засыпал
        play_timer = 0
        while vc.is_connected() and vc.is_playing() and play_timer < 600:
            await asyncio.sleep(2)
            play_timer += 2
        
        if vc.is_playing():
            print("Время сессии истекло. Обновление аудиопотока...", flush=True)
            vc.stop()
            
        if source:
            try:
                source.cleanup()
            except Exception:
                pass
                
        print("Перезапуск цикла воспроизведения...", flush=True)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен и готов к стримингу!", flush=True)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Ошибка входа в голосовой канал: {e}", flush=True)

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
