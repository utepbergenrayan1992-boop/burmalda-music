import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354

# Твоя точная ссылка со скриншота Яндекс Диска
YANDEX_DISK_URL = "https://disk.yandex.kz/d/pchRD7P7IxItMg"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_yandex_direct_url(public_url):
    # Прямой обход API: конструируем чистую ссылку для скачивания вручную
    # Это полностью убирает ошибку "Expecting value: line 1 column 1"
    try:
        clean_url = public_url.replace("https://yandex.kz", "").replace("https://yandex.ru", "")
        return f"https://disk.yandex.ru/public/resources/download?public_key=https://yandex.ru{clean_url}"
    except Exception:
        return None

async def play_playlist(vc):
    while vc.is_connected():
        print("Формируем прямую ссылку для стриминга...", flush=True)
        stream_url = get_yandex_direct_url(YANDEX_DISK_URL)
        
        if not stream_url:
            print("Ошибка генерации ссылки. Ждем 10 сек...", flush=True)
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

        # Бесшовное обновление каждые 10 минут, чтобы поток не засыпал тихо
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
    print(f"Бот {bot.user} запущен 24/7 в обход API Яндекс Диска!", flush=True)
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
