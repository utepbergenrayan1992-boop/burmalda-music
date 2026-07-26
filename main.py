import os
import discord
from discord.ext import commands, tasks

# Считываем токен из переменной окружения на Railway
TOKEN = os.getenv('TOKEN')

# ID текстового канала, куда бот будет писать каждый час (вставьте ваш ID)
CHANNEL_ID = 1405955231828676755

# Никнейм цели (имя пользователя, а не отображаемое имя)
TARGET_USERNAME = "bebra777_228_69610"

intents = discord.Intents.default()
intents.members = True  # Нужно для поиска пользователя по серверу

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен на Railway!')
    # Запускаем таймер, если он еще не запущен
    if not hourly_check.is_running():
        hourly_check.start()

# Задача выполняется ровно раз в час
@tasks.loop(minutes=1)
async def hourly_check():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Ошибка: Канал не найден. Проверьте CHANNEL_ID.")
        return

    target_member = None
    
    # Ищем пользователя по его username среди участников сервера
    async for member in channel.guild.fetch_members(limit=None):
        if member.name == TARGET_USERNAME:
            target_member = member
            break

    # Если нашли — пингуем, если нет — пишем обычным текстом
    if target_member:
        await channel.send(f'{target_member.mention} бабье')
    else:
        await channel.send(f'@{TARGET_USERNAME} бабье')
    print(f"Отправлено уведомление для {TARGET_USERNAME}")

# Запуск бота через токен из панели Railway
if __name__ == "__main__":
    bot.run(TOKEN)
