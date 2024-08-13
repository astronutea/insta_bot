from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F
from sqlalchemy import select, func, delete
from middleware import ChatTypeFilter
from database.models import User
from aiogram_i18n import I18nContext, LazyFilter
from routers.start import start

router = Router()




@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "open_help_menu_cb" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    builder = InlineKeyboardBuilder()
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("button_pass_tutoring_btn"), callback_data="open_tutoring_1"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("button_support_btn"), url="https://t.me/cryptobamboobot"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
        )
    await callback_query.message.edit_text(i18n.get("help_btn_message"),reply_markup=builder.as_markup())

@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "open_tutoring_" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    page_num = int(callback_query.data.split("_")[-1])
 
    builder = InlineKeyboardBuilder()
    if page_num == 1:
        builder.add( 
            types.InlineKeyboardButton(text=i18n.get("right_tutoring_btn"), callback_data="open_tutoring_" + str(page_num + 1))
            )
        
    elif page_num == 6:
        builder.add( 
            types.InlineKeyboardButton(text=i18n.get("left_tutoring_btn"), callback_data="open_tutoring_" + str(page_num - 1)) 
            )
    else:
        builder.row(
            types.InlineKeyboardButton(text=i18n.get("left_tutoring_btn"), callback_data="open_tutoring_" + str(page_num - 1)),
            types.InlineKeyboardButton(text=i18n.get("right_tutoring_btn"), callback_data="open_tutoring_" + str(page_num + 1))
            )
    if page_num == 1 or page_num == 6:
        builder.add( 
            types.InlineKeyboardButton(text=i18n.get("end_tutoring_btn"), callback_data="return_to_start")
            )
    else:
        builder.row(types.InlineKeyboardButton(text=i18n.get("end_tutoring_btn"), callback_data="return_to_start"))

    await callback_query.message.edit_text(i18n.get(f"tutoring_msg_number_{page_num}"),reply_markup=builder.as_markup())