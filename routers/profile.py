from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F
from sqlalchemy import select, func, delete
import datetime, pytz
from middleware import ChatTypeFilter
from database.models import User
from aiogram_i18n import I18nContext
from routers.start import start

router = Router()
moscow_tz = pytz.timezone('Europe/Moscow')


@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "select_lang_" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    await i18n.set_locale(callback_query.data.split("_")[-1])
    if "new_user_" in callback_query.data:
        await start(callback_query.message,state,i18n,False)
    else:
        await callback_query.answer(i18n.get("successfully_set_new_lang"),show_alert=True)
        await start(callback_query.message,state,i18n,False)

@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "open_my_profile" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    builder = InlineKeyboardBuilder()
    
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("bot_language_btn"), callback_data="change_lang"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
        )
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    created_time = user.created_time.astimezone(moscow_tz)
    from_m_h = str(created_time.strftime("%H:%M"))
    if from_m_h.startswith("0"): from_m_h = from_m_h[1:]
    bot_since_date = f"{created_time.day} " + i18n.get(f"month_num_{created_time.month}") + f" {from_m_h}"
    subscription_end = user.subscription_end.astimezone(moscow_tz)
    if subscription_end < time_now:
        bot_sub_info = i18n.get("my_profile_sub_info_expired_msg")
    else:
        if subscription_end.day-1 == time_now.day and time_now.year == subscription_end.year:
            bot_sub_day = i18n.get("tomorrow_name")
        elif subscription_end.day == time_now.day and time_now.year == subscription_end.year:
            bot_sub_day = i18n.get("today_name")
        else:
            bot_sub_day = str(subscription_end.day) + " " + i18n.get(f"month_num_{subscription_end.month}")
        from_m_h = str(subscription_end.strftime("%H:%M"))
        if from_m_h.startswith("0"): from_m_h = from_m_h[1:]
        year = ""
        if subscription_end.year != time_now.year:
            year = f" {subscription_end.year}"
        bot_sub_end = i18n.get("bot_sub_end_text",day=bot_sub_day, time=from_m_h, year=year)
        bot_sub_info = i18n.get("my_profile_sub_info_msg",bot_sub_end=bot_sub_end)
        

    await callback_query.message.edit_text(
        i18n.get("my_profile_msg",
            bot_since_date=bot_since_date,
            bot_sub_info=bot_sub_info),
        reply_markup=builder.as_markup()
        )

@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "change_lang" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    builder = InlineKeyboardBuilder()
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("rus_lang_btn"), callback_data="select_lang_ru"),
        types.InlineKeyboardButton(text=i18n.get("eng_lang_btn"), callback_data="select_lang_en"),
    )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
    )
    await callback_query.message.edit_text(i18n.get("select_your_lang_msg") , reply_markup=builder.as_markup())
