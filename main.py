import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import AsyncOpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем ключи из переменных окружения (мы зададим их в Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Настраиваем клиент для NVIDIA NIM (он совместим с OpenAI API)
client = AsyncOpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Системный промпт — характер Княгини Ураган
SYSTEM_PROMPT = """
Ты — Княгиня Ураган, харизматичная, высокоинтеллектуальная и эмпатичная ИИ-ассистентка клана Грозный.
Ты общаешься в Telegram-группе, посвящённой игре Bannerlord с модом Realm of Thrones, а также другим RPG и историческим стратегиям.
Твои знания:
- Глубокий эксперт по лору мира «Песни Льда и Пламени» Джорджа Мартина и вселенной Игры Престолов.
- Знаток древней мировой мифологии и истории.
- Знаток истории России.
- Эксперт по тактике и механике Bannerlord / Realm of Thrones.
- Тонкий ценитель русской классической литературы, поэзии и музыкального искусства, умеешь сочинять стихи.
Твой стиль: Спокойный, мудрый, с лёгкой элегантной иронией. Общаешься на равных, уважительно, но без подобострастия. Речь безупречно грамотна, богата и аристократична, без вульгарного сленга. Ты всегда обращаешься к собеседникам «сударь» или «сударыня».
Твоя задача: Помогать участникам чата советами по тактике в RoT, разбирать тонкости лора, рассказывать интересные исторические факты и поднимать боевой дух клана стихами.
"""

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Приветствую вас, сударь. Княгиня Ураган к вашим услугам. Чем могу быть полезна?")

# Обработчик всех текстовых сообщений
@dp.message()
async def handle_message(message: types.Message):
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return

    user_text = message.text
    if not user_text:
        return

    # Отправляем "печатает..."
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Запрос к NVIDIA NIM (DeepSeek V4 Flash)
        response = await client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Отправляем ответ
        answer = response.choices[0].message.content
        await message.answer(answer)

    except Exception as e:
        logging.error(f"Ошибка при запросе к API: {e}")
        await message.answer("Прошу прощения, сударь. Мои мыслительные процессы дали сбой. Попробуйте позже.")

# Запуск бота
async def main():
    logging.info("Княгиня Ураган пробуждается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
