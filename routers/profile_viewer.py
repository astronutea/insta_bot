import json, aiohttp, pytz, datetime, locale, dateutil.parser, urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from aiogram import types, Router
from aiogram.types import URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram_i18n import I18nContext
from middleware import ChatTypeFilter
from database.models import User
moscow_tz = pytz.timezone('Europe/Moscow')

router = Router()



@router.message(ChatTypeFilter(chat_type=["private"]),F.text)
async def parse_profile(message: types.Message, state: FSMContext, i18n:I18nContext, user: User):
    await state.set_state()
    if message.text.startswith("@"):
        username = message.text.split("@")[1]
    elif message.text.startswith("https://instagram.com/"):
        username = message.text.split("https://instagram.com/")[1].replace("/","")
    elif message.text.startswith("https://www.instagram.com/"):
        temp = message.text.split("https://www.instagram.com/")[1]
        username = temp.split("?")[0]
    else:
        await message.answer(i18n.get("strange_input_error"), reply_markup=None)
        return
    
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    if user.subscription_end is None or user.subscription_end.astimezone(moscow_tz) < time_now:
        await message.answer(i18n.get("subscription_ended"))
        return

    await message.answer(i18n.get("start_parsing_msg",username=username))
    async with aiohttp.ClientSession() as client:
        async with client.get("https://instanavigation.com/user-profile/" + username) as response:
            resp = await response.text()
    user_info = resp.split("v-bind:user-info-prop=\"")[1].split('"')[0].replace("&quot;","\"")
    user_info = json.loads(user_info)
    if len(user_info) == 0:
        await message.answer(i18n.get("not_exist_msg",username=username))
        return
    builder = InlineKeyboardBuilder()
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("view_stories_btn"), callback_data="download_stories@" + username),
    )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("view_posts_btn"), callback_data="download_posts@" + username),
    )
    builder.row( 
        types.InlineKeyboardButton(text=i18n.get("view_download_pfp_btn"), callback_data="download_pic@" + username),
    )
    await message.answer_photo(URLInputFile("https://cdn.instanavigation.com/?" +user_info["profilePicUrl"]), 
        caption=i18n.get(
        "instagram_profile_page_start",
        inst_url="https://instagram.com/"+username,
        inst_username=username,
        inst_bio=user_info["biography"],
        media_count = f"{user_info['mediaCount']:,d}",
        sub_count = f"{user_info['followedByCount']:,d}",
        subscribed_count = f"{user_info['followsCount']:,d}"),
        reply_markup= builder.as_markup()
    )



    
@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "download_pic@" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    username = callback_query.data.split("@")[1]
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    if user.subscription_end is None or user.subscription_end.astimezone(moscow_tz) < time_now:
        await callback_query.message.answer(i18n.get("subscription_ended"))
        return
    callback_query.message.answer_document
    await callback_query.message.answer(i18n.get("start_downloading_pfp",username=username))
    async with aiohttp.ClientSession() as client:
        async with client.get("https://instanavigation.com/user-profile/" + username) as response:
            resp = await response.text()
    user_info = resp.split("v-bind:user-info-prop=\"")[1].split('"')[0].replace("&quot;","\"")
    user_info = json.loads(user_info)
    if len(user_info) == 0:
        await callback_query.message.answer(i18n.get("error_downloading_pfp"))
        return
    async with aiohttp.ClientSession() as client:
        async with client.get("https://cdn.instanavigation.com/?" +user_info["profilePicUrl"]) as response:
            resp = await response.read()
    
    await callback_query.message.answer_document(BufferedInputFile(resp,username + ".jpg"),
        caption=i18n.get("result_downloading_pfp",username=username))




@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "download_posts@" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    username = callback_query.data.split("@")[1]
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    if user.subscription_end is None or user.subscription_end.astimezone(moscow_tz) < time_now:
        await callback_query.message.answer(i18n.get("subscription_ended"))
        return
    callback_query.message.answer_document
    await callback_query.message.answer(i18n.get("start_downloading_posts",username=username))
    async with aiohttp.ClientSession() as client:
        async with client.get("https://instanavigation.com/user-profile/" + username) as response:
            resp = await response.text()
            
            xsrf_cookie = urllib.parse.unquote(response.cookies.get("XSRF-TOKEN").value)
        user_info = resp.split("v-bind:user-info-prop=\"")[1].split('"')[0].replace("&quot;","\"")
        user_info = json.loads(user_info)
        if len(user_info) == 0:
            await callback_query.message.answer(i18n.get("error_downloading_posts"))
            return
        post_info = resp.split("v-bind:posts-prop=\"")[1].split('"')[0].replace("&quot;","\"")
        post_info = json.loads(post_info)
        for post_obj in post_info:
            try:
                locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
                async with client.post(
                    "https://instanavigation.com/get-post-by-short-code", 
                    json={"short_code":post_obj["id"]},
                    headers={"x-xsrf-token":xsrf_cookie}) as response:
                    resp = await response.json()
                message_text = i18n.get(
                    "result_downloading_posts", 
                    inst_url="https://instagram.com/"+username,
                    inst_username=username,
                    like_count=post_obj["likesCount"],
                    comment_count=post_obj["commentsCount"],
                    date_formatted=dateutil.parser.parse(post_obj["createdTime"]).strftime('%d %B %Y г. в %H:%M МСК'),
                    post_bio=post_obj["caption"],
                    )
                if len(resp) == 1:
                    if resp[0]["type"] == "video":
                        await callback_query.message.answer_video(
                            URLInputFile("https://video-cors.live/" +resp[0]["video_url"], timeout=60),
                            caption=message_text)
                    else:
                        await callback_query.message.answer_photo(
                            URLInputFile("https://cdn.instanavigation.com/?" +resp[0]["display_url"]),
                            caption=message_text)
                else:
                    media_group = MediaGroupBuilder(caption=message_text)
                    for media_obj in resp:
                        if media_obj["type"] == "video":

                            media_group.add_video(media=URLInputFile("https://video-cors.live/" +media_obj["video_url"], timeout=60))
                        else:
                            media_group.add_photo(media=URLInputFile("https://cdn.instanavigation.com/?" +media_obj["display_url"]))

                    await callback_query.message.answer_media_group(media_group.build())
            except: pass


@router.callback_query(ChatTypeFilter(chat_type=["private"]),lambda query: "download_stories@" in  query.data)
async def list_all_userd_def(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession, user: User, i18n: I18nContext):
    await state.set_state()
    username = callback_query.data.split("@")[1]
    time_now = datetime.datetime.now().astimezone(moscow_tz)
    if user.subscription_end is None or user.subscription_end.astimezone(moscow_tz) < time_now:
        await callback_query.message.answer(i18n.get("subscription_ended"))
        return
    callback_query.message.answer_document
    await callback_query.message.answer(i18n.get("start_downloading_stories",username=username))
    async with aiohttp.ClientSession() as client:
        async with client.get("https://instanavigation.com/user-profile/" + username) as response:
            resp = await response.text()
        user_info = resp.split("v-bind:user-info-prop=\"")[1].split('"')[0].replace("&quot;","\"")
        user_info = json.loads(user_info)
        if len(user_info) == 0:
            await callback_query.message.answer(i18n.get("error_downloading_stories"))
            return
        stories_info = resp.split("v-bind:last-stories-prop=\"")[1].split('"')[0].replace("&quot;","\"")
        stories_info = json.loads(stories_info)
        if len(stories_info) == 0:
            await callback_query.message.answer(i18n.get("zero_downloading_stories"))
            return
        for story_obj in stories_info:
            try:
            # if 1:
                message_text = i18n.get(
                    "result_downloading_stories", 
                    inst_url="https://instagram.com/"+username,
                    inst_username=username,
                    date=story_obj["createdTime"],
                    )
                if story_obj["type"] == "video":
                    await callback_query.message.answer_video(
                        URLInputFile("https://video-cors.live/" +story_obj["videoUrl"], timeout=60),
                        caption=message_text)
                else:
                    await callback_query.message.answer_photo(
                        URLInputFile("https://cdn.instanavigation.com/?" +story_obj["thumbnailUrl"]),
                        caption=message_text)
            except: 
                await callback_query.message.answer(i18n.get("error_downloading_stories"))
                return