#!/usr/bin/env python3

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

# =========================
# TOKEN (KEYIN O‘ZGARTIRASAN)
# =========================
BOT_TOKEN = "8739255554:AAFXT8sAitgT_gwI9FCs17crl4w6syLieq4"
QUESTIONS_FILE = "questions.txt"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================
# QUESTIONS LOAD
# =========================
def load_questions(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return []

    questions = []
    blocks = content.split("+++++")

    for block in blocks:
        parts = [p.strip() for p in block.split("=====")]
        if len(parts) < 3:
            continue

        q_text = parts[0]
        options = []
        correct = 0

        for i, p in enumerate(parts[1:]):
            if p.startswith("#"):
                correct = len(options)
                options.append(p[1:].strip())
            else:
                options.append(p.strip())

        if len(options) >= 2:
            questions.append({
                "question": q_text,
                "options": options,
                "correct": correct
            })

    return questions


QUESTIONS = load_questions(QUESTIONS_FILE)


# =========================
def shuffle_question(q):
    options = q["options"][:]
    correct_text = options[q["correct"]]

    random.shuffle(options)
    new_correct = options.index(correct_text)

    return {
        "question": q["question"],
        "options": options,
        "correct": new_correct
    }


# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Quiz Bot\nJami savol: {len(QUESTIONS)}\n/quiz"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    selected = random.sample(QUESTIONS, 10)
    context.user_data["session"] = {
        "questions": [shuffle_question(q) for q in selected],
        "i": 0,
        "score": 0,
        "chat_id": update.effective_chat.id
    }

    await send_question(update.effective_chat.id, context)


async def send_question(chat_id, context):
    s = context.user_data["session"]
    i = s["i"]

    if i >= len(s["questions"]):
        await finish(chat_id, context)
        return

    q = s["questions"][i]

    await context.bot.send_poll(
        chat_id=chat_id,
        question=q["question"][:300],
        options=q["options"],
        type=Poll.QUIZ,
        correct_option_id=q["correct"],
        is_anonymous=False,
        open_period=30
    )


async def poll_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = context.user_data.get("session")
    if not s:
        return

    q = s["questions"][s["i"]]

    if update.poll_answer.option_ids[0] == q["correct"]:
        s["score"] += 1

    s["i"] += 1
    await asyncio.sleep(1)
    await send_question(s["chat_id"], context)


async def finish(chat_id, context):
    s = context.user_data["session"]
    score = s["score"]
    total = len(s["questions"])

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🏁 Tugadi!\nScore: {score}/{total}"
    )

    context.user_data.clear()


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /quiz")


# =========================
def main():
    if BOT_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("TOKEN qo‘yilmagan!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(PollAnswerHandler(poll_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Bot ishga tushdi")
    app.run_polling()


if __name__ == "__main__":
    main()
