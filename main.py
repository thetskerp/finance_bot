import asyncio
import logging


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from config.config import Config, load_config
from handlers.user import user_router
from database.db import init_db


async def main():
    config: Config = load_config()

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )

    logging.info('Starting BOT')

    init_db(config.db.db_name)

    #local_telegram_server = TelegramAPIServer.from_base(config.proxy_session.session)

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        #server = local_telegram_server,
    )

    

    dp = Dispatcher()
    dp['config'] = config
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())