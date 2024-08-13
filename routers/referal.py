from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.command import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import F
from sqlalchemy import select, func, delete
import pytz
from middleware import ChatTypeFilter
from database.models import User
from aiogram_i18n import I18nContext, LazyFilter
# from keyboard import return_to_profile_kb
# from states import all_states
from routers.start import start

router = Router()
moscow_tz = pytz.timezone('Europe/Moscow')



@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "open_referal_system" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    # new_lang = callback_query.data.split("_")[-1]
    # user.lang = new_lang
    # await session.commit()
    builder = InlineKeyboardBuilder()
    
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("ref_withdraw_money"), callback_data="ref_withdraw_money"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
        )
    await callback_query.message.edit_text(
        i18n.get("referal_system_msg",
            tg_bot_username="cryptobamboo001_bot",
            referal_id=user.ref_secured_id,
            rub_balance=user.ref_balance),
        reply_markup=builder.as_markup(), disable_web_page_preview=True
        )


@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "ref_withdraw_money" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    builder = InlineKeyboardBuilder()
    
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
    )
    await callback_query.message.edit_text(
        i18n.get("ref_withdraw_money_msg",tg_username="cryptobamboobot"),
        reply_markup=builder.as_markup()
    )
