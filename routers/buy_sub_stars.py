from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types, Router
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import F
from sqlalchemy import select, func, delete
import config, datetime, pytz
from middleware import ChatTypeFilter
from database.models import User
from aiogram_i18n import I18nContext, LazyFilter
from routers.start import start

router = Router()
moscow_tz = pytz.timezone('Europe/Moscow')




@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "start_payment_stars" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    subscription_end = user.subscription_end.astimezone(moscow_tz)
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    if subscription_end < time_now:
        bot_sub_info = i18n.get("buy_sub_info_expired_msg")
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
        bot_sub_info = i18n.get("buy_sub_info_msg",bot_sub_end=bot_sub_end)
    builder = InlineKeyboardBuilder()
    for star_obj in config.star_prices:
        builder.row( 
            types.InlineKeyboardButton(text=i18n.get(f"stars_buy_sub_period_btn_{star_obj}",time=i18n.get(f"invoice_label_time_{star_obj}"),star_price=config.star_prices[star_obj]["star_price"]), callback_data=f"stars_buy_sub_period_btn_{star_obj}"),
        )
    await callback_query.message.edit_text(
        i18n.get("start_payment_msg",
                 buy_sub_info_msg = bot_sub_info,
                 tg_username = "cryptobamboobot"),
                reply_markup=builder.as_markup()
            )


@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "stars_buy_sub_period_btn_" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    
    sub_period = callback_query.data.split("_")[-1]
    if sub_period not in config.star_prices:
        return
    amount = config.star_prices[sub_period]["star_price"]
    prices = [LabeledPrice(label="XTR", amount=amount)]

    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n.get("payment_n_xtr_btn",amount=amount),
        pay=True
    )
    builder.button(
        text=i18n.get("cancel_payment_stars_btn"),
        callback_data="return_2_start_from_invoice"
    )
    builder.adjust(1)

    await callback_query.message.answer_invoice(
        title=i18n.get("stars_invoice_label_info", time=i18n.get(f"invoice_label_time_{sub_period}")),
        description=i18n.get("star_invoice_desc"),
        prices=prices,
        provider_token="",
        payload= f"{amount}_stars",
        currency="XTR",
        reply_markup=builder.as_markup()
    )

@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
    i18n: I18nContext,
):
    is_in_prices = False
    
    for i in config.star_prices:
        if config.star_prices[i]["star_price"] == pre_checkout_query.total_amount:
            is_in_prices=True
            break
    if not is_in_prices:
        await pre_checkout_query.answer(
            ok=False,
            error_message=i18n.get("star_payment_is_not_available_btn")
        )
    else:
        await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(
    message: types.Message,
    i18n: I18nContext,
    session: AsyncSession,
    user: User
):
    sub_period = ""
    for i in config.star_prices:
        if config.star_prices[i]["star_price"] == message.successful_payment.total_amount:
            sub_period  = i
            break
    if sub_period == "":
        return
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    if user.subscription_end.astimezone(moscow_tz) < time_now:
        user.subscription_end = time_now + datetime.timedelta(days=config.star_prices[sub_period]["days"])
    else:
        user.subscription_end = user.subscription_end + datetime.timedelta(days=config.star_prices[sub_period]["days"])
    await session.commit()

    await message.answer(
        i18n.get(
            "star_invoice_result",
            day=i18n.get(f"invoice_label_time_{sub_period}")
        ),
    )

@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "return_2_start_from_invoice" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    await callback_query.message.delete()
    await start(callback_query.message, state, i18n, False, True)