import os
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354

# === СЮДА ВСТАВЬ СВОЮ ПУБЛИЧНУЮ ССЫЛКУ НА ЯНДЕКС ДИСК ===
YANDEX_DISK_URL = "https://disk.yandex.kz/d/pchRD7P7IxItMg"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_yandex_direct_url(public_url):
    # Делаем официальный запрос к API Яндекса для извлечения прямого аудиопотока
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_url}"
    try:
        response = requests.get(api_url).json()
        return response.get('href')
    except Exception as e:
        print(f"Ошибка получения потока Яндекса: {e}", flush=True)
        return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Запрос прямого потока из Яндекс Диска...", flush=True)
        stream_url = get_yandex_direct_url(YANDEX_DISK_URL)
        
        if not stream_url:
            print("Ошибка: Яндекс отказал в доступе. Проверь ссылку!", flush=True)
            await asyncio.sleep(10)
            continue

        print("Запуск бесконечного воспроизведения трека BURMALDA FM...", flush=True)
        source = None
        try:
            source = discord.FFmpegPCMAudio(
                stream_url, 
                before_options=FFMPEG_OPTIONS['before_options'], 
                options=FFMPEG_OPTIONS['options']
            )
            vc.play(source)
        except Exception as e:
            print(f"Ошибка FFmpeg при чтении Яндекса: {e}", flush=True)
            if source:
                source.cleanup()
            await asyncio.sleep(5)
            continue

        while vc.is_connected() and vc.is_playing():
            await asyncio.sleep(2)
        
        if source:
            try:
                source.cleanup()
            except Exception:
                pass
                
        print("Круг завершён. Перезапуск аудиопотока...", flush=True)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен в режиме стриминга с Яндекс Диска!", flush=True)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Ошибка подключения к войсу: {e}", flush=True)

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
