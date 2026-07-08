import asyncio
import logging
import os
import random
import json
import aiofiles
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

# Load environment variables from .env if present
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    bot_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    logger.warning("BOT_TOKEN is not set in .env. Using dummy token for initialization.")

bot = Bot(token=bot_token)
dp = Dispatcher()

ANSWERS = {
    "Какие из наших готовых кейсов чаще всего подходят для малого и среднего бизнеса?": (
        "🧠 [Анализ слоя Context / Кейсы]: Исходя из нашей базы данных, для сегмента SMB оптимальны два решения:\n"
        "ИИ-микросервис для колл-центров — автоматизирует разбор заказов из звонков, убирая рутинный ввод данных менеджерами.\n"
        "Мультиагентная система SMM — автоматизирует ведение Telegram-каналов. Оба решения укладываются в наш лимит до 200 000 рублей и не требуют от клиента сложной ИТ-инфраструктуры."
    ),
    "Проверь статус тестового сервера. Мы сможем развернуть на нем пилотный ИИ-модуль для тестов?": (
        "📊 [Мониторинг слоя Data]: Текущий статус инфраструктуры Aivion: • Тестовый сервер: ONLINE (Локальный дата-центр в РФ, полное соответствие 152-ФЗ). • Менеджер процессов: PM2 активен. Ограничений для деплоя пилотных коробочных версий нет. Контур готов к изолированному тестированию."
    ),
    "Выведи базовый регламент для проведения бесплатного экспресс-аудита клиента.": (
        "📃 [Запрос из слоя Context / Регламенты]: Согласно стандарту Aivion, перед началом работы мы проводим бесплатный ТЗ-Review или экспресс-аудит. Базовый чек-лист вопросов для клиента:\n"
        "- Где сейчас ФОТ утекает в ручной труд? (Где сотрудники делают однотипные действия руками?)\n"
        "- Какие CRM или базы данных используются? (amoCRM, Битрикс24, 1С, таблицы)\n"
        "- Есть ли ограничения Службы Безопасности по передаче данных во внешние API?"
    ),
    "Как мы решаем проблему санкционных блокировок зарубежных LLM в наших проектах?": (
        "🛡️ [Безопасность / Слой Context]: В архитектуру систем Aivion заложен принцип гибридной отказоустойчивости. При проектировании мы настраиваем оркестратор: сложная аналитика идет на ведущие модели, но при их недоступности или блокировке прокси система автоматически переключается (fallback) на российские аналоги или локальные нейросети, развернутые в контуре РФ."
    ),
    "Какие коробочные продукты у нас сейчас полностью упакованы и готовы к быстрой интеграции?": (
        "📦 [Сквозной анализ базы знаний]: На текущий момент (08.07.2026) в рамках стратегии «Троянский конвейер» полностью упакован и готов к деплою ИИ-квалификатор лидов. Модуль точечно интегрируется в текущие процессы компании и закрывает дыры, куда утекает рабочее время сотрудников. Код полностью готов к передаче заказчику."
    )
}

async def simulate_rag_search():
    """Simulates a RAG search by asynchronously reading layer files and logging."""
    logger.info("=== STARTING RAG SEARCH SIMULATION ===")

    context_data = {}
    data_data = {}

    try:
        async with aiofiles.open("layer_context.json", mode="r", encoding="utf-8") as f:
            content = await f.read()
            context_data = json.loads(content)
            logger.info("Loaded layer_context.json successfully.")
    except Exception as e:
        logger.error(f"Error loading layer_context.json: {e}")

    try:
        async with aiofiles.open("layer_data.json", mode="r", encoding="utf-8") as f:
            content = await f.read()
            data_data = json.loads(content)
            logger.info("Loaded layer_data.json successfully.")
    except Exception as e:
        logger.error(f"Error loading layer_data.json: {e}")

    logger.info("--- PROMPT ASSEMBLY LOG ---")
    logger.info(f"System Context: {context_data.get('agency_name')} | Tech: {context_data.get('tech_stack')}")
    infra = data_data.get('internal_infrastructure', {})
    logger.info(f"Infrastructure State: Server - {infra.get('test_server_status')}, Zone - {infra.get('deployment_zone')}")
    logger.info("=== RAG SEARCH SIMULATION COMPLETE ===")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {message.from_user.full_name}! Бот-симулятор Aivion готов к работе. Отправь мне запрос.")

@dp.message(F.text)
async def message_handler(message: Message) -> None:
    delay = random.uniform(5, 10)
    logger.info(f"Received message. Starting RAG simulation with a delay of {delay:.2f} seconds.")

    # We use ChatActionSender to hold the TYPING action for the duration of our sleep
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        # 1. Asynchronously read from json layers and log prompt assembly
        await simulate_rag_search()

        # 2. Wait for the random delay between 5 and 10 seconds
        await asyncio.sleep(delay)

    text = message.text.strip()

    if text in ANSWERS:
        await message.answer(ANSWERS[text])
    else:
        # Fallback for unrecognized questions (not explicitly requested, but good practice)
        await message.answer("Я не нашел релевантного ответа в слоях Context и Data по твоему запросу.")

async def main() -> None:
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
