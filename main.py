import os
import asyncio
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("BOT_TOKEN")
VOICE_CHANNEL_ID = 1530548841324089354
YANDEX_DISK_URL = "https://disk.yandex.kz/d/pchRD7P7IxItMg"

MUSIC_FOLDER = "playlist"
LOCAL_TRACK_PATH = os.path.join(MUSIC_FOLDER, "music.mp3")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {'options': '-vn'}

def download_file_from_yandex():
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)
        
    # Если файл уже скачан и весит нормально, не качаем его заново
    if os.path.exists(LOCAL_TRACK_PATH) and os.path.getsize(LOCAL_TRACK_PATH) > 100 * 1024 * 1024:
        print("Файл уже скачан локально и готов к работе!", flush=True)
        return True

    print("Подключаемся к публичному зеркалу Яндекса для скачивания...", flush=True)
    # Используем прямое зеркало виджета, которое не блокирует зарубежные хостинги
    direct_url = f"https://yandex.ru{YANDEX_DISK_URL}"
    
    try:
        response = requests.get(direct_url, timeout=15)
        if response.status_code == 200:
            download_url = response.json().get('href')
            print("Начинаем прямое скачивание 441 Мб на жесткий диск хостинга... Подожди 1-2 минуты.", flush=True)
            
            with requests.get(download_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(LOCAL_TRACK_PATH, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024): # Блоками по 1 Мб
                        if chunk:
                            f.write(chunk)
            print("Файл успешно скачан и сохранен в папку playlist локально!", flush=True)
            return True
        else:
            print(f"Зеркало вернуло код {response.status_code}: {response.text}", flush=True)
            return False
    except Exception as e:
        print(f"Ошибка при скачивании файла: {e}", flush=True)
        return False

async def play_playlist(vc):
    print("Проверка наличия локального файла...", flush=True)
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, download_file_from_yandex)
    
    if not success or not os.path.exists(LOCAL_TRACK_PATH):
        print("Не удалось подготовить локальный файл. Повтор через 10 секунд...", flush=True)
        await asyncio.sleep(10)
        bot.loop.create_task(play_playlist(vc))
        return

    while vc.is_connected():
        print(f"Запуск локального трека из папки: {LOCAL_TRACK_PATH}", flush=True)
        source = None
        try:
            source = discord.FFmpegPCMAudio(LOCAL_TRACK_PATH, options=FFMPEG_OPTIONS['options'])
            vc.play(source)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}", flush=True)
            await asyncio.sleep(5)
            continue

        # Спокойно ждем окончания, так как файл играет прямо с диска сервера Render
        while vc.is_connected() and vc.is_playing():
            await asyncio.sleep(2)

        if source:
            try:
                source.cleanup()
            except Exception:
                pass
            
        print("Локальный трек завершился. Запуск по новой...", flush=True)
        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен в чистом локальном режиме!", flush=True)
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
            bot.loop.create_task(play_playlist(vc))
        except Exception as e:
            print(f"Не удалось подключиться: {e}", flush=True)

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
