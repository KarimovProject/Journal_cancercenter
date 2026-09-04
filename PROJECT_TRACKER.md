# Loyiha Holati va Rivojlanish Jurnali (Project Tracker)

> ⚠️ **ESKIRGAN — bu fayl faqat tarixiy ma'lumot uchun qoldirilgan.**
> Loyihaning joriy holati, keyingi qadamlari va tuzoqlari **`GOALS.md`** da.
> Yangilashni ham o'sha yerda qiling; bu faylni yangilamang.

Ushbu fayl loyihada avval nima qilingani, hozirda qanday jarayon ketyotgani va kelajakda nimalar qilinishi kerakligini kuzatib borish uchun mo'ljallangan (kesh vazifasini o'taydi).

## 🟢 Avval qilingan ishlar (Bajarilgan)
- **Boshlang'ich Sozlamalar:** Django loyihasi yaratilgan va asosiy ilovalar (journal, oncoscience) sozlab chiqilgan.
- **Infratuzilma (Deployment):** Docker va Kubernetes (k8s.yaml) orqali loyiha jangovar serverga (Traefik bilan birga) joylashtirilgan.
- **CI/CD:** GitHub Actions orqali avtomatik deployment quvuri (deploy.yml) yo'lga qo'yilgan.
- **Sozlamalarni Modullashtirish:** Monolit settings.py fayli muhitlarga ajratildi (ase.py, dev.py, prod.py, sqlite.py).
- **Ma'lumotlar Bazasini Migratsiyasi:** Loyiha SQLite'dan to'liq PostgreSQL'ga o'tkazildi (avtomatik dumpdata va loaddata skripti orqali). Barcha 137 ta ob'ekt muvaffaqiyatli ko'chirildi.

## 🟡 Hozirgi holat (Jarayonda)
- **Tekshiruv bosqichi:** Platforma yangi ma'lumotlar bazasi (PostgreSQL) bilan qanday ishlayotganini jonli serverda to'liq tekshirish va monitoring qilish.
- **Kichik xatolarni tuzatish:** Foydalanuvchilar tomonidan yoki test jarayonida chiqishi mumkin bo'lgan kichik bug'larni aniqlash va darhol bartaraf etish.

## 🔴 Kelajakdagi rejalar (Qilinishi kerak)
- [x] Ma'lumotlar bazasini avtomatik zaxiralash (Kunlik Postgres zaxirasi Telegram bot orqali yuborilishi Kubernetes CronJob orqali yo'lga qo'yilgan).
- [x] Saytning ishlash tezligi va xavfsizligini (SEO, SSL qoidalari, CORS) yana bir bor chuqur tahlil qilish (Audit o'tkazildi, Xavfsizlik sarlavhalari va Sitemap qo'shildi).
- [x] Foydalanuvchilar tomonidan berilgan yangi funksional talablarni (Feature requests) ro'yxatga olish va ishlab chiqish (Taklif yuborish sahifasi va Admin paneli yaratildi).

*Eslatma: Ushbu fayl loyiha ustida ishlovchi dasturchilar (yoki sun'iy intellekt agentlari) loyiha tarixini va joriy maqsadlarni tushunib olishi uchun har bir muhim o'zgarishdan so'ng yangilab borilishi tavsiya etiladi.*
