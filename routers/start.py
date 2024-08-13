from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram import types, Router
from aiogram.filters.command import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from middleware import ChatTypeFilter
from database.models import User

router = Router()

@router.message(ChatTypeFilter(chat_type=["private"]),CommandStart())
async def start(message: types.Message, state: FSMContext, i18n:I18nContext, is_new_user: bool, new_msg = False): #, session: AsyncSession
    await state.set_state()
    if message.text is not None and message.text == "/start":
        new_msg = True
    if is_new_user:
        builder = InlineKeyboardBuilder()
        builder.row( 
            types.InlineKeyboardButton(text=i18n.get("rus_lang_btn"), callback_data="new_user_select_lang_ru"),
            types.InlineKeyboardButton(text=i18n.get("eng_lang_btn"), callback_data="new_user_select_lang_en"),
        )
        await message.answer(i18n.get("select_your_lang_msg") , reply_markup=builder.as_markup())
        return
    builder = InlineKeyboardBuilder()
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("pay_for_subscription_btn"), callback_data="open_pay_for_subscription"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("my_profile_btn"), callback_data="open_my_profile"),
        types.InlineKeyboardButton(text=i18n.get("open_help_btn"), callback_data="open_help_menu_cb"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("referal_system_btn"), callback_data="open_referal_system"),
        types.InlineKeyboardButton(text=i18n.get("our_channel_btn_link"), url="https://t.me/snbbot_news"),
        )
    if new_msg:
        await message.answer(i18n.get("welcome_start_msg"), reply_markup=builder.as_markup())
    else: 
        await message.edit_text(i18n.get("welcome_start_msg"), reply_markup=builder.as_markup())

@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "return_to_start" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    await start(callback_query.message, state, i18n, False)
    
@router.message(ChatTypeFilter(chat_type=["private"]),Command("faq"))
async def faq_cmd_def(message: types.Message, state: FSMContext, i18n:I18nContext):
    builder = InlineKeyboardBuilder()
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
        )
    await message.answer(i18n.get("faq_cmd_msg"), reply_markup=builder.as_markup())
