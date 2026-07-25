import discord
from discord.ext import tasks
import random
import asyncio

#
# Вставьте сюда ID текстового канала, где бот должен спамить (включите режим разработчика в ДС -> ПКМ по каналу -> Копировать ID)
CHANNEL_ID = 1041431136687112193  

intents = discord.Intents.default()
intents.members = True # Разрешаем доступ к списку пользователей

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен и готов обзываться!')
    # Запускаем фоновую задачу
    random_ping.start()

@tasks.loop(hours=2) # По умолчанию проверяет каждый час. Можно изменить на minutes=30 или seconds=10 для теста
async def random_ping():
    # Шанс срабатывания (например, 30% при каждой проверке, чтобы момент был реально рандомным)
    if random.random() < 0.2: 
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            # Получаем список всех людей на сервере, исключая ботов
            members = [m for m in channel.guild.members if not m.bot]
            
            if members:
                victim = random.choice(members)
                # Отправляем сообщение с упоминанием
                await channel.send(f'{victim.mention} БАБЬЕ БЛЯТЬ')

# Запуск бота
bot.run(TOKEN)
