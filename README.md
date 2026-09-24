# 🎬 Kinobot — Telegram kino boti

Aiogram 3 + PostgreSQL asosida yozilgan kino boti. Majburiy kanal obunasi,
kino kodi bo'yicha qidiruv, TOP filmlar, sevimlilar, VIP obuna (admin
tasdiqlaydigan chek orqali) va bot ichidagi admin panel.

## 📁 Loyiha tuzilishi

```
kinobot/
├── main.py                 # botni ishga tushiruvchi fayl
├── config.py                # .env dan sozlamalarni o'qiydi
├── states.py                 # FSM holatlari
├── requirements.txt
├── .env.example
├── database/
│   ├── models.py            # jadvallar (User, Movie, Channel, VipPlan ...)
│   ├── db.py                 # engine/session
│   └── requests.py            # barcha DB so'rovlari
├── handlers/
│   ├── user.py                # /start, qidiruv, TOP, sevimlilar
│   ├── vip.py                  # VIP sotib olish oqimi
│   └── admin.py                 # admin panel
├── keyboards/
│   ├── user_kb.py
│   └── admin_kb.py
└── filters/
    ├── is_admin.py
    └── subscription.py         # majburiy obunani tekshirish
```

---

## 1-qadam: Kerakli narsalar

- Python 3.11+
- PostgreSQL server (mahalliy yoki masalan [Neon](https://neon.tech),
  [Railway](https://railway.app), [ElephantSQL](https://www.elephantsql.com) — bepul variantlar)
- [@BotFather](https://t.me/BotFather) orqali yaratilgan bot tokeni
- Telegram ID'ingiz (@userinfobot ga `/start` yozing)

## 2-qadam: Loyihani mahalliy sozlash

```bash
# virtual muhit yaratish
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# kutubxonalarni o'rnatish
pip install -r requirements.txt

# .env faylini yaratish
cp .env.example .env
```

`.env` faylini oching va to'ldiring:

```
BOT_TOKEN=BotFather bergan token
SUPER_ADMIN_ID=sizning telegram ID'ingiz
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

## 3-qadam: PostgreSQL bazasini yaratish

Mahalliy PostgreSQL bo'lsa:

```bash
psql -U postgres -c "CREATE DATABASE kinobot_db;"
psql -U postgres -c "CREATE USER kinobot WITH PASSWORD 'kinobot_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE kinobot_db TO kinobot;"
```

Jadvallar bot birinchi ishga tushganda `main.py` ichidagi `init_db()` orqali
avtomatik yaratiladi — qo'lda SQL yozish shart emas.

## 4-qadam: Botni ishga tushirish

```bash
python main.py
```

Konsolda `✅ Baza tayyor, bot ishga tushmoqda...` chiqsa — hammasi ishlayapti.
Telegram'da botga `/start` yozing, keyin o'zingizga `/admin` yozib admin
panelni oching (faqat `SUPER_ADMIN_ID` yoki qo'shilgan adminlar uchun ishlaydi).

### Admin panelda nima qilish mumkin
- 🎬 Kino qo'shish — video yuboriladi → kod, nom, tavsif, VIP-only belgisi so'raladi
- 🗑 Kino o'chirish — kod bo'yicha
- 📢 Kanal qo'shish — botni kanalga admin qilib qo'shing, so'ng kanaldan
  xabar forward qiling (majburiy obuna shu kanal uchun ishlaydi)
- 📋 Kanallar ro'yxati — yoqish/o'chirish, o'chirish
- 📊 Statistika — foydalanuvchilar, VIP, kinolar soni
- 📨 Xabar yuborish — barcha foydalanuvchilarga broadcast
- 👑 VIP so'rovlar — foydalanuvchi chek yuborganda avtomatik keladi,
  ✅/❌ tugmalari bilan tasdiqlanadi/rad etiladi
- 💳 VIP tariflar — `/addplan` orqali yangi tarif (nom, narx, muddat) qo'shiladi

---

## 🐙 GitHub'ga yuklash — bosqichma-bosqich

### 1. Git o'rnatilganini tekshiring
```bash
git --version
```
Yo'q bo'lsa: Windows — [git-scm.com](https://git-scm.com), Mac — `brew install git`,
Linux — `sudo apt install git`.

### 2. GitHub'da yangi repository yarating
1. [github.com](https://github.com) ga kiring → yuqori o'ng burchakda **+** → **New repository**
2. **Repository name**: masalan `kinobot`
3. **Private** ni tanlang (bot tokeningiz ochilib qolmasligi uchun tavsiya)
4. README, .gitignore, license qo'shmang (bizda allaqachon bor) → **Create repository**
5. Ochilgan sahifadagi repo manzilini saqlab qo'ying, masalan:
   `https://github.com/USERNAME/kinobot.git`

### 3. Loyiha papkasida Git'ni ishga tushiring
Terminalda loyiha papkasiga o'ting (`kinobot` papkasi ichida turing) va:

```bash
git init
git add .
git commit -m "Boshlang'ich versiya: kinobot"
```

> ⚠️ `.env` fayli **hech qachon** yuklanmaydi — u `.gitignore` ichida.
> Tokeningiz va parollaringiz shu tufayli GitHub'ga tushmaydi. Tekshiring:
> `git status` buyrug'ida `.env` ko'rinmasligi kerak.

### 4. GitHub repository'ni ulash va yuklash

```bash
git branch -M main
git remote add origin https://github.com/USERNAME/kinobot.git
git push -u origin main
```

`USERNAME/kinobot` o'rniga o'zingiznikini yozing. Birinchi push'da GitHub
login/parol yoki *Personal Access Token* so'rashi mumkin (2021-yildan beri
oddiy parol ishlamaydi — GitHub → Settings → Developer settings →
Personal access tokens orqali token yarating va parol o'rniga shuni kiriting).

### 5. Keyingi o'zgarishlarni yuklash

Kodga o'zgartirish kiritgan sayin:

```bash
git add .
git commit -m "O'zgarish tavsifi"
git push
```

### 6. (Ixtiyoriy) Serverga joylashtirish

Repo tayyor bo'lgach, serverda (VPS, Railway, Render va h.k.):

```bash
git clone https://github.com/USERNAME/kinobot.git
cd kinobot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # va to'ldiring
python main.py
```

Doimiy ishlashi uchun `systemd` service yoki `screen`/`tmux`/`pm2`
(Node emas, lekin `pm2 start "python main.py" --name kinobot` ham ishlaydi)
yoki `nohup python main.py &` dan foydalanishingiz mumkin.

---

## Keyingi qadam: Mini App

Hozirgi versiya to'liq tugmali (Reply/Inline keyboard) ishlaydi. Keyinroq
Telegram **Mini App** (Web App) qo'shish uchun bot ichida `WebAppInfo` bilan
tugma qo'shiladi va HTML/React frontend `main.py`dagi handlerlar bilan bir xil
`database/requests.py` funksiyalaridan foydalanadi — bazani qayta yozish
shart bo'lmaydi.
