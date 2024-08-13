from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F
import pytz
from middleware import ChatTypeFilter
from database.models import User
from aiogram_i18n import I18nContext
from routers.start import start

router = Router()
moscow_tz = pytz.timezone('Europe/Moscow')



@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "open_pay_for_subscription" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    builder = InlineKeyboardBuilder()
    
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("star_payment_type"), callback_data="start_payment_stars"),
        )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("go_back_btn"), callback_data="return_to_start"),
        )
    await callback_query.message.edit_text(
        i18n.get("pay_sub_start_btn"),
        reply_markup=builder.as_markup()
        )
