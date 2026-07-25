import os
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354
YANDEX_DISK_URL = "https://yandex.kz"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Железобетонные настройки для онлайн-стриминга аудиопотока
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_direct_stream_url():
    """Получает чистую прямую ссылку через официальное API Яндекс Диска"""
    base_url = "https://yandex.net"
    try:
        # params принудительно кодирует URL, убирая ошибку JSON парсинга (line 1 column 1)
        response = requests.get(base_url, params={'public_key': YANDEX_DISK_URL}, timeout=10)
        if response.status_code == 200:
            return response.json().get('href')
        print(f"Яндекс API вернул ошибку {response.status_code}", flush=True)
    except Exception as e:
        print(f"Ошибка сети Яндекс API: {e}", flush=True)
    return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запрашиваем ссылку у Яндекса...", flush=True)
        loop = asyncio.get_event_loop()
        stream_url = await loop.run_in_executor(None, get_direct_stream_url)

        if not stream_url:
            print("Ссылка пустая. Ждем 15 секунд во избежание ошибки 4006...", flush=True)
            await asyncio.sleep(15)
            continue

        print("Запуск трансляции трека в голосовой канал...", flush=True)
        source = None
        try:
            source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            vc.play(source)
        except Exception as e:
            print(f"Сбой FFmpeg при воспроизведении: {e}", flush=True)
            await asyncio.sleep(10)
            continue

        # Удерживаем цикл, пока трек играет
        while vc.is_connected() and vc.is_playing():
            await asyncio.sleep(2)

        if source:
            try:
                source.cleanup()
            except Exception:
                pass
        
        await asyncio.sleep(2)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен на Railway 24/7!", flush=True)
    
    # Принудительная инициализация Opus перед коннектом
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
