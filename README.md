# Oncoscience — Ilmiy jurnal platformasi

Respublika Ixtisoslashtirilgan Onkologiya va Radiologiya Ilmiy-Amaliy Tibbiyot
Markazi (cancercenter.uz) uchun **mustaqil** ilmiy jurnal platformasi. Springer
Link, ESMO Annals of Oncology, MDPI Current Oncology kabi akademik jurnal
saytlariga o'xshash tarzda qurilgan.

Bu asosiy `cancercenter.uz` saytidan **alohida** Django loyihasi: o'z kodbazasi,
o'z bazasi va o'z deploymenti bilan. Taklif etilgan domen: `science.cancercenter.uz`.

## Texnologik stack

- **Django 5.2** + **Django REST Framework**
- **PostgreSQL** (production) / SQLite (lokal development uchun avtomatik fallback)
- Django templates (server-side rendering), responsive, akademik dizayn
- Ko'p tillilik: **uz / ru / en** (har bir modelda `*_uz/_ru/_en` maydonlari)
- `whitenoise` (static), `gunicorn` + `nginx` (production)

## Asosiy imkoniyatlar

- **Maqolalar**: ro'yxat + filtrlash (yo'nalish/yil/muallif), qidiruv, sahifalash,
  to'liq sahifa (annotatsiya, PDF, DOI, APA iqtibos, mualliflar, o'xshash maqolalar)
- **Ilmiy kengash**, **kafedralar**, **konferensiyalar** (kelayotgan/o'tgan),
  **aspirantura/ordinatura**, **grantlar**, **mualliflar uchun** sahifasi
- **Django admin** orqali barcha kontentni boshqarish (PDF yuklash, `order` bilan tartiblash)
- **DRF API** — asosiy sayt bilan integratsiya uchun (masalan "so'nggi maqolalar" bloki)
- **SEO / Open Graph** meta teglar + Google Scholar (`citation_*`) meta teglari

## URL struktura

| URL | Sahifa |
|-----|--------|
| `/ilm-fan/` | Bosh sahifa |
| `/ilm-fan/maqolalar/` | Maqolalar (filtr/qidiruv/pagination) |
| `/ilm-fan/maqolalar/<slug>/` | Maqola sahifasi |
| `/ilm-fan/mualliflar/<slug>/` | Muallif profili |
| `/ilm-fan/ilmiy-kengash/` | Ilmiy kengash |
| `/ilm-fan/kafedralar/` | Kafedralar |
| `/ilm-fan/konferensiyalar/` , `/ilm-fan/konferensiyalar/<slug>/` | Konferensiyalar |
| `/ilm-fan/aspirantura/` , `/ilm-fan/ordinatura/` | Ta'lim dasturlari |
| `/ilm-fan/grantlar/` | Grantlar |
| `/ilm-fan/mualliflar-uchun/` | Maqola yuborish qoidalari |
| `/admin/` | Boshqaruv paneli |
| `/api/` | REST API (articles, categories, authors, conferences) |

## Lokal ishga tushirish (Windows)

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# .env ixtiyoriy — DB_NAME bo'lmasa SQLite ishlatiladi
copy .env.example .env

.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_data          # namuna ma'lumotlar (ixtiyoriy)
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

Sayt: http://127.0.0.1:8000/ilm-fan/ · Admin: http://127.0.0.1:8000/admin/

> Lokal `seed_data` demo superuser yaratmaydi — `createsuperuser` orqali yarating.

## Production (VPS: Gunicorn + Nginx + PostgreSQL)

```bash
# 1. Kod va muhit
git clone <repo> /var/www/oncoscience && cd /var/www/oncoscience
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
cp .env.example .env   # to'ldiring: SECRET_KEY, DEBUG=False, DB_*, ALLOWED_HOSTS

# 2. PostgreSQL
sudo -u postgres createuser oncoscience -P
sudo -u postgres createdb oncoscience -O oncoscience

# 3. Baza va static
./venv/bin/python manage.py migrate
./venv/bin/python manage.py collectstatic --noinput
./venv/bin/python manage.py createsuperuser

# 4. Gunicorn + Nginx
sudo cp deploy/gunicorn.service /etc/systemd/system/oncoscience.service
sudo systemctl daemon-reload && sudo systemctl enable --now oncoscience
sudo cp deploy/nginx.conf /etc/nginx/sites-available/oncoscience
sudo ln -s /etc/nginx/sites-available/oncoscience /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
# HTTPS: sudo certbot --nginx -d science.cancercenter.uz
```

## Ko'p tillilik

Kontent maydonlari bazada `title_uz/ru/en` ko'rinishida saqlanadi. Model
`.title`, `.abstract` kabi propertylar faol tilga qarab qiymatni qaytaradi
(uz → fallback). Til almashtirish tugmasi headerda (`/i18n/setlang/`).

## Asosiy sayt bilan integratsiya (2-bosqich)

Bazalar bog'lanmaydi. Asosiy `cancercenter.uz` sayti REST API'ni iste'mol qiladi:

```
GET /api/articles/?ordering=-publication_date        # so'nggi maqolalar
GET /api/articles/<slug>/                             # to'liq ma'lumot
GET /api/categories/  ·  /api/authors/  ·  /api/conferences/
```

CORS `.env` dagi `CORS_ALLOWED_ORIGINS` orqali boshqariladi. `Author` modeli
`external_doctor_id` maydoni kelajakda shifokorlar bazasi bilan sinxronlash uchun.

## Keyingi bosqichlar

- WordPress "Ilm-fan" kontentini import qilish (management command)
- CrossRef orqali citation tracker; DOI generatsiya integratsiyasi
- PubMed/Scholar indekslash uchun qo'shimcha meta teglar
