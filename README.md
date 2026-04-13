# 🧬 Odam Anatomiyasi Quiz Bot

Telegram Quiz formatida anatomiya testlarini o'tkazuvchi bot.

---

## 🚀 O'rnatish va ishlatish

### 1-qadam: Token olish
1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Botingizga nom bering (masalan: `AnatomiyaQuizBot`)
4. Username bering (masalan: `anatomiya_quiz_bot`)
5. BotFather sizga **TOKEN** beradi — uni saqlang

### 2-qadam: Fayllarni tayyorlash
```
anatomy_quiz_bot/
├── bot.py                    ← Asosiy bot fayli
├── requirements.txt          ← Kutubxonalar
└── questions.txt             ← Savollar fayli (sizning faylingiz)
```

Savol faylini `bot.py` bilan bir papkaga qo'ying va `bot.py` ichida yo'lni to'g'rilang:
```python
QUESTIONS = load_questions("questions.txt")
```

### 3-qadam: Tokenni kiritish
`bot.py` faylini oching va:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```
o'rniga BotFather bergan tokenni yozing:
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 4-qadam: Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 5-qadam: Botni ishga tushirish
```bash
python bot.py
```

---

## 🎮 Bot komandалари

| Komanda | Vazifasi |
|---------|----------|
| `/start` | Botni boshlash, yordam |
| `/quiz` | 10 ta savol bilan test boshlash |
| `/quiz20` | 20 ta savol bilan test boshlash |
| `/quiz50` | 50 ta savol bilan test boshlash |
| `/score` | Joriy natijani ko'rish |
| `/stop` | Testni to'xtatish |

---

## 📊 Baholash tizimi

| Foiz | Baho |
|------|------|
| 90-100% | 🏆 A'lo |
| 75-89% | 👍 Yaxshi |
| 60-74% | 😊 Qoniqarli |
| 40-59% | 😐 O'rtacha |
| 0-39% | 😔 Qoniqarsiz |

---

## 📁 Savol fayli formati

```
Savol matni?
=====
#To'g'ri javob    ← # belgisi to'g'ri javobni belgilaydi
=====
Noto'g'ri javob 1
=====
Noto'g'ri javob 2
=====
Noto'g'ri javob 3


+++++


Keyingi savol?
...
```

---

## 🖥 Server yoki kompyuterda doim ishlatish (ixtiyoriy)

**Windows (fon jarayon sifatida):**
```
pythonw bot.py
```

**Linux/Mac (fon jarayon):**
```bash
nohup python bot.py &
```

**Yoki `screen` orqali:**
```bash
screen -S quizbot
python bot.py
# Ctrl+A, D — ajralish
```

---

## ⚠️ Muhim eslatmalar

- Bot **private chat** da yaxshi ishlaydi
- Guruh chat uchun botga **admin** huquqi bering
- Har bir test boshlanishida savollar **aralashtiriladi**
- Har bir savol uchun **30 soniya** vaqt beriladi
