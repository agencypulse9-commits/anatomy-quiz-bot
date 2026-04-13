#!/usr/bin/env python3
"""
Odam Anatomiyasi Quiz Bot — Tuzatilgan versiya
- Javoblar aralashtiriladi
- To'g'ri javob indeksi dinamik saqlanadi
"""

import logging
import random
import asyncio
from telegram import Update, Poll
from telegram.ext import (
    Application,
    CommandHandler,
    PollAnswerHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =============================================
# SOZLAMALAR
# =============================================
BOT_TOKEN = "8739255554:AAFXT8sAitgT_gwI9FCs17crl4w6syLieq4"
QUESTIONS_FILE = "questions.txt"

# =============================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# =============================================
# SAVOLLARNI O'QISH
# =============================================
def load_questions(filepath: str) -> list:
    questions = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"Fayl topilmadi: {filepath}")
        return []

    blocks = content.split("+++++")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        parts = [p.strip() for p in block.split("=====")]
        if len(parts) < 3:
            continue

        question_text = parts[0].strip()
        if not question_text:
            continue

        options = []
        correct_index = 0

        for i, part in enumerate(parts[1:]):
            part = part.strip()
            if not part:
                continue
            if part.startswith("#"):
                correct_index = len(options)
                options.append(part[1:].strip())
            else:
                options.append(part)

        options = [o[:100] for o in options if o][:10]

        if len(options) >= 2 and 0 <= correct_index < len(options):
            questions.append({
                "question": question_text,
                "options": options,
                "correct": correct_index,
            })

    logger.info(f"Yuklandi: {len(questions)} ta savol")
    return questions


QUESTIONS = load_questions(QUESTIONS_FILE)


# =============================================
# JAVOBLARNI ARALASHTIRISH — ASOSIY TUZATISH
# =============================================
def shuffle_question(q: dict) -> dict:
    """
    Javob variantlarini aralashtiradi.
    To'g'ri javob MATNI bo'yicha yangi indeks topiladi.
    """
    options = q["options"][:]
    correct_text = options[q["correct"]]  # to'g'ri javobning MATNI

    random.shuffle(options)  # variantlarni aralashtirish

    new_correct = options.index(correct_text)  # yangi pozitsiya

    return {
        "question": q["question"],
        "options": options,
        "correct": new_correct,  # yangi to'g'ri indeks
    }


# =============================================
# KOMANDALAR
# =============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n"
        "🧬 *Odam Anatomiyasi Quiz Bot*\n\n"
        "▶️ /quiz — 10 ta savol\n"
        "🔢 /quiz20 — 20 ta savol\n"
        "🎯 /quiz50 — 50 ta savol\n"
        "📚 /quizall — Barcha savollar\n"
        "📊 /score — Joriy natija\n"
        "⏹ /stop — Testni to'xtatish\n\n"
        f"📚 Jami: *{len(QUESTIONS)} ta savol*",
        parse_mode="Markdown"
    )


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int):
    if not QUESTIONS:
        await update.message.reply_text("❌ Savollar yuklanmadi. questions.txt faylini tekshiring!")
        return

    context.user_data.clear()
    context.user_data["chat_id"] = update.effective_chat.id

    count = min(count, len(QUESTIONS))
    selected_raw = random.sample(QUESTIONS, count)

    # Har bir savol uchun javoblarni aralashtirish
    selected = [shuffle_question(q) for q in selected_raw]

    context.user_data["session"] = {
        "questions": selected,
        "current": 0,
        "score": 0,
        "total": count,
        "answered": False,
    }

    await update.message.reply_text(
        f"🚀 *Test boshlandi!*\n"
        f"📝 Jami: *{count} ta savol*\n\n"
        f"Har bir savolga 30 soniya ichida javob bering! ⏱",
        parse_mode="Markdown"
    )

    await send_next_question(update.effective_chat.id, context)


async def quiz_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_quiz(update, context, 10)

async def quiz_20(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_quiz(update, context, 20)

async def quiz_50(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_quiz(update, context, 50)

async def quiz_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_quiz(update, context, len(QUESTIONS))


# =============================================
# SAVOL YUBORISH
# =============================================
async def send_next_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("session")
    if not session:
        return

    idx = session["current"]
    total = session["total"]

    if idx >= total:
        await finish_quiz(chat_id, context)
        return

    q = session["questions"][idx]

    question_text = f"📌 {idx + 1}/{total}\n\n{q['question']}"
    if len(question_text) > 300:
        question_text = question_text[:297] + "..."

    session["answered"] = False

    try:
        await context.bot.send_poll(
            chat_id=chat_id,
            question=question_text,
            options=q["options"],
            type=Poll.QUIZ,
            correct_option_id=q["correct"],   # aralashtirилgan indeks
            is_anonymous=False,
            open_period=30,
        )
        logger.info(f"Savol {idx+1}/{total} | To'g'ri: '{q['options'][q['correct']]}'")

    except Exception as e:
        logger.error(f"Poll xatosi (savol {idx+1}): {e}")
        session["current"] += 1
        await send_next_question(chat_id, context)


# =============================================
# JAVOB QABUL QILISH
# =============================================
async def poll_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    session = context.user_data.get("session")

    if not session:
        return

    if session.get("answered"):
        return
    session["answered"] = True

    idx = session["current"]
    if idx >= session["total"]:
        return

    if not answer.option_ids:
        return

    q = session["questions"][idx]
    selected = answer.option_ids[0]

    if selected == q["correct"]:
        session["score"] += 1

    session["current"] += 1

    await asyncio.sleep(1.5)

    chat_id = context.user_data.get("chat_id", answer.user.id)
    await send_next_question(chat_id, context)


# =============================================
# YAKUNLASH
# =============================================
async def finish_quiz(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("session")
    if not session:
        return

    score = session["score"]
    total = session["total"]
    percent = (score / total * 100) if total > 0 else 0

    if percent >= 90:
        grade, emoji = "A'lo! 🏆", "🌟"
    elif percent >= 75:
        grade, emoji = "Yaxshi! 👍", "✅"
    elif percent >= 60:
        grade, emoji = "Qoniqarli 😊", "📗"
    elif percent >= 40:
        grade, emoji = "O'rtacha 😐", "📙"
    else:
        grade, emoji = "Qoniqarsiz 😔", "📕"

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"{emoji} *Test yakunlandi!*\n\n"
            f"✅ To'g'ri javoblar: *{score}/{total}*\n"
            f"📈 Foiz: *{percent:.1f}%*\n"
            f"🎓 Baho: *{grade}*\n\n"
            f"Qayta urinish: /quiz"
        ),
        parse_mode="Markdown"
    )

    context.user_data.clear()


async def score_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("session")
    if not session:
        await update.message.reply_text("❌ Aktiv test yo'q. /quiz bilan boshlang!")
        return

    current = session["current"]
    total = session["total"]
    sc = session["score"]
    percent = (sc / current * 100) if current > 0 else 0

    await update.message.reply_text(
        f"📊 *Joriy natija:*\n\n"
        f"✅ To'g'ri: *{sc}/{current}*\n"
        f"📈 Foiz: *{percent:.1f}%*\n"
        f"⏳ Qoldi: *{total - current} ta*",
        parse_mode="Markdown"
    )


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = context.user_data.get("session")
    if not session:
        await update.message.reply_text("❌ Aktiv test yo'q.")
        return

    sc = session["score"]
    current = session["current"]
    total = session["total"]
    context.user_data.clear()

    await update.message.reply_text(
        f"⏹ *Test to'xtatildi!*\n\n"
        f"📊 Natija: {sc}/{current} (jami {total} dan)\n\n"
        f"Qayta boshlash: /quiz",
        parse_mode="Markdown"
    )


async def save_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat:
        context.user_data["chat_id"] = update.effective_chat.id


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Komandadan foydalaning:\n"
        "/quiz — Test boshlash\n"
        "/start — Yordam"
    )


# =============================================
# MAIN
# =============================================
def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("=" * 50)
        print("❌ BOT_TOKEN kiritilmagan!")
        print('bot.py da BOT_TOKEN = "..." qatorini to\'ldiring')
        print("=" * 50)
        return

    if not QUESTIONS:
        print(f"❌ Savollar yuklanmadi! '{QUESTIONS_FILE}' faylini tekshiring.")
        return

    print(f"✅ {len(QUESTIONS)} ta savol yuklandi")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, save_chat_id), group=-1)
    app.add_handler(PollAnswerHandler(save_chat_id), group=-1)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_10))
    app.add_handler(CommandHandler("quiz20", quiz_20))
    app.add_handler(CommandHandler("quiz50", quiz_50))
    app.add_handler(CommandHandler("quizall", quiz_all))
    app.add_handler(CommandHandler("score", score_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))

    app.add_handler(PollAnswerHandler(poll_answer_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    print("🤖 Bot ishga tushdi! Ctrl+C — to'xtatish")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
