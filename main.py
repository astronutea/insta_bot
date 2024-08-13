import asyncio
import config
from database.db import async_session
from middleware import UserManager, DbSessionMiddleware, UserMiddleware
from aiogram import Bot, Dispatcher
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from routers import buy_sub_stars, start, profile, help, referal, buy_sub, buy_sub_rub, buy_sub_crypto, profile_viewer
from aiogram.client.default import DefaultBotProperties
bot = Bot(token=config.tg_token, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()




async def main():
    dp.include_routers(
        start.router,
        profile.router,
        help.router,
        referal.router,
        buy_sub_stars.router,
        buy_sub.router,
        buy_sub_rub.router,
        buy_sub_crypto.router,
        profile_viewer.router,
    )
    mw = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}",
        ),
        manager=UserManager(),
    )
    dp.update.outer_middleware(DbSessionMiddleware(
        async_session
    ))
    dp.update.outer_middleware(UserMiddleware())
    mw.setup(dispatcher=dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())