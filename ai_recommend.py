import json
import httpx
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ANTHROPIC_API_KEY
from database.requests import (
    get_all_movies_brief, get_movie_by_code, increment_views,
    get_user_favorites, get_user, is_user_vip,
)
from keyboards.user_kb import main_menu_kb, movie_actions_kb
from states import AIRecommend

router = Router()

ANTHROPIC_MODEL = "claude-sonnet-4-5"


@router.message(F.text == "🤖 AI tavsiya")
async def ai_recommend_start(message: Message, state: FSMContext):
    if not ANTHROPIC_API_KEY:
        await message.answer("🤖 AI tavsiya funksiyasi hozircha sozlanmagan.")
        return
    await state.set_state(AIRecommend.waiting_mood)
    await message.answer(
        "🤖 Hozir kayfiyatingiz yoki qanday kino ko'rgingiz kelayotganini yozing.\n"
        "Masalan: <i>\"Bugun kayfiyatim tushkun, kuldiradigan yengil narsa ko'rmoqchiman\"</i>\n\n"
        "(Bekor qilish uchun /cancel)"
    )


@router.message(AIRecommend.waiting_mood)
async def ai_recommend_process(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())
        return

    await state.clear()
    movies = await get_all_movies_brief(limit=200)
    if not movies:
        await message.answer("😔 Hozircha bazada kinolar yo'q, tavsiya bera olmayman.")
        return

    catalog_text = "\n".join(
        f"- kod:{m.code} | nomi:{m.title} | janr:{m.genre or '—'} | yil:{m.year or '—'} | "
        f"tavsif:{(m.description or '')[:150]}"
        for m in movies
    )

    system_prompt = (
        "Sen kino tavsiya qiluvchi yordamchisan. Foydalanuvchi o'z kayfiyati yoki "
        "istagini yozadi. Sizga berilgan RO'YXATDAN faqat bitta eng mos kinoni tanlang. "
        "Ro'yxatdan tashqari kino taklif qilmang. Faqat quyidagi JSON formatida javob bering, "
        "boshqa hech qanday matn qo'shmang:\n"
        '{"code": "kino_kodi", "reason": "nega bu kino mos kelishi haqida 1-2 gapli tushuntirish o\'zbek tilida"}'
    )

    user_prompt = f"Kinolar ro'yxati:\n{catalog_text}\n\nFoydalanuvchi holati: {message.text}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": 300,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            data = resp.json()
    except Exception:
        await message.answer("❌ AI xizmatiga ulanishda xatolik yuz berdi. Keyinroq urinib ko'ring.")
        return

    try:
        text_block = next(b["text"] for b in data["content"] if b["type"] == "text")
        cleaned = text_block.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        parsed = json.loads(cleaned)
        code = parsed["code"]
        reason = parsed.get("reason", "")
    except Exception:
        await message.answer("❌ AI javobini o'qib bo'lmadi. Qaytadan urinib ko'ring.")
        return

    movie = await get_movie_by_code(code)
    if not movie:
        await message.answer("😔 Mos kino topilmadi, boshqa so'z bilan urinib ko'ring.")
        return

    if movie.is_vip_only and not await is_user_vip(message.from_user.id):
        await message.answer(
            f"🤖 AI sizga <b>{movie.title}</b> ni tavsiya qildi, lekin bu kino faqat VIP uchun!"
        )
        return

    user = await get_user(message.from_user.id)
    favs = await get_user_favorites(user.id) if user else []
    is_fav = any(m.id == movie.id for m in favs)

    caption = f"🤖 <b>AI tavsiyasi:</b> {reason}\n\n🎬 <b>{movie.title}</b>"
    if movie.genre:
        caption += f"\n🎭 Janr: {movie.genre}"
    await message.answer_video(
        video=movie.file_id, caption=caption, reply_markup=movie_actions_kb(movie, is_fav),
    )
    await increment_views(movie.id)
