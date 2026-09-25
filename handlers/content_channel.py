import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from filters.is_admin import IsAdmin
from keyboards.admin_kb import admin_menu_kb
from database.requests import (
    set_content_channel, get_content_channel, is_content_channel,
    get_movie_by_code, add_movie,
)
from states import SetContentChannel

router = Router()


@router.message(IsAdmin(), F.text == "📥 Kontent kanal")
async def set_content_channel_start(message: Message, state: FSMContext):
    current = await get_content_channel()
    current_text = f"\n\nHozirgi kontent kanal: <b>{current.title}</b>" if current else ""
    await state.set_state(SetContentChannel.waiting_forward)
    await message.answer(
        "📥 Botni kanalga <b>admin</b> qilib qo'shing, so'ng shu kanaldan istalgan "
        "xabarni shu yerga forward qiling.\n\n"
        "Shundan keyin \"Kino qo'shish\" orqali yuklagan har bir video avtomatik "
        "shu kanalga ham joylanadi va tomoshabinlarga aynan shu kanaldan yuboriladi.\n\n"
        f"{current_text}\n\n(Bekor qilish uchun /cancel)"
    )


@router.message(SetContentChannel.waiting_forward, F.forward_from_chat)
async def set_content_channel_process(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    chat = message.forward_from_chat
    try:
        await bot.get_chat_member(chat.id, bot.id)
    except Exception:
        await message.answer("❌ Bot ushbu kanalda admin emas. Avval botni admin qiling.", reply_markup=admin_menu_kb())
        return

    await set_content_channel(chat_id=chat.id, title=chat.title)
    await message.answer(
        f"✅ Kontent kanal o'rnatildi: {chat.title}\n\n"
        f"Endi \"Kino qo'shish\" orqali yuklagan videolar avtomatik shu kanalga ham tushadi.",
        reply_markup=admin_menu_kb(),
    )


@router.message(SetContentChannel.waiting_forward)
async def set_content_channel_wrong(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu_kb())
        return
    await message.answer("❗️ Iltimos, kontent kanalidan biror xabarni forward qiling. (Bekor qilish uchun /cancel)")


# ---------- Kanalga to'g'ridan-to'g'ri video joylansa ham avtomatik qo'shish ----------

@router.channel_post(F.video)
async def auto_add_movie_from_channel(message: Message):
    if not await is_content_channel(message.chat.id):
        return

    caption = message.caption or ""
    match = re.match(r"^#?(\w{2,20})[\s\-:]+(.+)", caption.strip(), re.DOTALL)
    if not match:
        return

    code = match.group(1).strip()
    title = match.group(2).strip().split("\n")[0][:255]

    existing = await get_movie_by_code(code)
    if existing:
        return

    await add_movie(
        code=code, title=title, file_id=message.video.file_id,
        channel_message_id=message.message_id,
    )
