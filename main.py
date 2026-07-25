import os
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354

# === СЮДА ВСТАВЬ СВОЮ ССЫЛКУ НА ЯНДЕКС ДИСК ===
YANDEX_DISK_URL = "https://disk.yandex.kz/d/pchRD7P7IxItMg"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_yandex_direct_url(public_url):
    api_url = f"https://yandex.net{public_url}"
    try:
        response = requests.get(api_url).json()
        return response.get('href')
    except Exception as e:
        print(f"Ошибка API Яндекса: {e}", flush=True)
        return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Обновляем прямую ссылку из Яндекс Диска...", flush=True)
        stream_url = get_yandex_direct_url(YANDEX_DISK_URL)
        
        if not stream_url:
            print("Ошибка: Не удалось получить ссылку. Ждем 10 сек...", flush=True)
            await asyncio.sleep(10)
            continue

        print("Запуск стриминга трека BURMALDA FM...", flush=True)
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

        # Защита от зависания: крутим цикл, но не дольше 10 минут (600 сек) за один раз
        play_timer = 0
        while vc.is_connected() and vc.is_playing() and play_timer < 600:
            await asyncio.sleep(2)
            play_timer += 2
        
        # Принудительно чистим поток, чтобы обновить ссылку на следующем круге
        if vc.is_playing():
            print("Время сессии истекло. Принудительное обновление потока...", flush=True)
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
    print(f"Бот {bot.user} запущен 24/7 с авто-обновлением потока Яндекс Диска!", flush=True)
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
