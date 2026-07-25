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

# Настройки FFmpeg для стабильного стриминга без скачивания на диск
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_direct_stream_url():
    """Получает прямую ссылку на скачивание/стриминг через API Яндекс Диска"""
    base_url = "https://yandex.net"
    try:
        # Корректный запрос к API Яндекса для публичной ссылки
        response = requests.get(f"{base_url}?public_key={YANDEX_DISK_URL}", timeout=10)
        if response.status_code == 200:
            return response.json().get('href')
        print(f"Яндекс API вернул код {response.status_code}: {response.text}", flush=True)
    except Exception as e:
        print(f"Ошибка при получении ссылки от Яндекса: {e}", flush=True)
    return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запрашиваем прямую ссылку у Яндекса...", flush=True)
        loop = asyncio.get_event_loop()
        stream_url = await loop.run_in_executor(None, get_direct_stream_url)

        if not stream_url:
            print("Ссылка не получена. Повтор через 10 секунд...", flush=True)
            await asyncio.sleep(10)
            continue

        print("Запуск потокового воспроизведения аудио...", flush=True)
        source = None
        try:
            source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            vc.play(source)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}", flush=True)
            await asyncio.sleep(5)
            continue

        # Ожидаем окончания трека
        while vc.is_connected() and vc.is_playing():
            await asyncio.sleep(2)

        if source:
            try:
                source.cleanup()
            except Exception:
                pass
        print("Поток завершился. Перезапуск соединения...", flush=True)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен на Railway!", flush=True)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Не удалось подключиться к каналу: {e}", flush=True)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        print("Бота кикнули из канала. Пытаемся зайти снова...", flush=True)
        await asyncio.sleep(5)
        channel = bot.get_channel(VOICE_CHANNEL_ID)
        if channel:
            try:
                vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
                bot.loop.create_task(play_playlist(vc))
            except Exception:
                pass

bot.run(TOKEN)
