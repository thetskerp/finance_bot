import asyncio
import logging


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import parse_mode


from config.config import Config, load_config
from handlers.user import user_router


async def main():
    config: Config = load_config()

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )

    logging.info('Starting BOT')

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    pass

if __name__ == '__main__':
    asyncio.run(main())