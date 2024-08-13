from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
import datetime, pytz, base58, random
from sqlalchemy import select
from database.models import User
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.managers import BaseManager
moscow_tz = pytz.timezone('Europe/Moscow')

class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list], chat_id = None):
        self.chat_type = chat_type
        self.chat_id = chat_id

    async def __call__(self, message_raw: Message) -> bool:
        message = message_raw
        if "aiogram.types.callback_query.CallbackQuery" in str(type(message)):
            message = message_raw.message
        chat_id_checker = False
        if isinstance(self.chat_type, str):
            chat_id_checker =( message.chat.type == self.chat_type)
        else:
            chat_id_checker = ( message.chat.type in self.chat_type)
        if not chat_id_checker:
            return False
            
        if self.chat_id == None:
            return True
        else:
            return str(self.chat_id) == str(message.chat.id)

class UserManager(BaseManager):
    async def set_locale(self, locale: str, session: AsyncSession) -> None:
        pass
    async def get_locale(self) -> str:
        return "default"

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool):
        super().__init__()
        self.session_pool = session_pool
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)

class UserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        message = None
        if "pre_checkout_query" in dict(event) and event.pre_checkout_query is not None:
            chat_tg_id = event.pre_checkout_query.from_user.id
        elif event.callback_query is not None:
            message = event.callback_query.message
            chat_tg_id = event.callback_query.message.chat.id
        elif "message" in dict(event) and "chat" in dict(event.message): 
            message = event.message
            chat_tg_id = event.message.chat.id
        
        user_obj = await data['session'].scalars(select(User).where(User.tg_id == chat_tg_id))
        user_obj = user_obj.first()
        if user_obj is None:
            moscow_dt = datetime.datetime.now()
            user_obj = User(
                tg_id = chat_tg_id,
                lang = "ru",
                created_time=moscow_dt,
                subscription_end=moscow_dt+datetime.timedelta(days=3),
                ref_secured_id=base58.b58encode(random.randbytes(6)).decode("utf-8") + str(chat_tg_id)[-2:] 
            )
            data["session"].add(user_obj)
            await data["session"].commit()
            data["is_new_user"] = True
        else:
            data["is_new_user"] = False
        if message is not None:
            if message.text is not None and message.text.startswith("/start ref_") and len(message.text.split("_")[-1]) <= 16:
                ref_id = message.text.split("_")[-1]
                if user_obj.refered_by is None and (await data['session'].scalars(select(User).where(User.ref_secured_id == ref_id))):
                    user_obj.refered_by = ref_id
                    await data["session"].commit()

        data["user"] = user_obj
        return await handler(event, data)

class UserManager(BaseManager):
    async def set_locale(self, locale: str, session: AsyncSession, user: User) -> None:
        user.lang = locale
        await session.commit()
    async def get_locale(self, user: User) -> str:
        return user.lang

