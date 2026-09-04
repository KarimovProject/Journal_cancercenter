# GOALS.md — Loyihaning yagona holat manbai

> **Har bir sessiya shu fayldan boshlanadi.** Ish boshlashdan oldin uni to'liq
> o'qing; ish tugagach — "Bajarilgan ishlar" va "Keyingi qadamlar" bo'limlarini
> yangilang. Sana formati: `YYYY-MM-DD` (nisbiy sana yozmang — "kecha", "o'tgan
> hafta" keyingi sessiyada ma'nosini yo'qotadi).

**Oxirgi yangilanish:** 2026-09-04

---

## 1. Loyiha haqida

**Central Asian Cancer Sciences** — onkologiya va radiologiya bo'yicha ilmiy
jurnal platformasi (RIOR IATM). Maqola yuborish, taqrizlash (peer review),
nashr qilish va tahririyat paneli.

| | |
|---|---|
| Stack | Django + HTMX (SPA emas, server-rendered) |
| Ilovalar | `journal/` (asosiy), `core/`, `oncoscience/` (settings/urls) |
| Sozlamalar | `oncoscience/settings/` — `base.py`, `dev.py`, `prod.py`, `sqlite.py` |
| Standart | `manage.py` → `oncoscience.settings.dev` (`DEBUG=True`, SQLite) |
| Prod DB | PostgreSQL (`prod.py`, env orqali) |
| Frontend | `templates/` + bitta `static/css/style.css` |
| Deploy | Docker + Kubernetes (`k8s.yaml`) + GitHub Actions (`.github/`) |
| Tillar | uz / ru / en (`locale/`, `LocaleMiddleware`) |

### Ishga tushirish va tekshirish

```bash
venv/Scripts/python.exe manage.py check                 # konfiguratsiya
venv/Scripts/python.exe manage.py runserver 8000        # dev server
venv/Scripts/python.exe manage.py test journal          # testlar (56 ta)
```

URL'lar til prefiksi bilan: bosh sahifa `/` → `/ilm-fan/` ga redirect bo'ladi.

---

## 2. Bajarilgan ishlar

### Infratuzilma (2026 yil boshi)
- Django loyihasi, `journal` + `oncoscience` ilovalari
- Docker + Kubernetes + Traefik bilan jangovar serverga joylashtirish
- GitHub Actions orqali avtomatik deployment
- `settings.py` muhitlarga ajratildi (base/dev/prod/sqlite)
- SQLite → PostgreSQL migratsiyasi (prod uchun)
- Kunlik Postgres zaxirasi — Kubernetes CronJob + Telegram bot
- Xavfsizlik auditi: security headers, CORS, sitemap
- Taklif yuborish (feedback) sahifasi va admin paneli

### Frontend qayta ishlash (2026-09-03)
Faqat `static/css/style.css`, `templates/base.html`, `templates/journal/home.html`,
`templates/journal/partials/_alerts_signup.html`,
`templates/journal/dashboard/submit_article.html` o'zgartirildi.
Python kodi va sozlamalarga tegilmagan.

**Yuklash tezligi**
- Dark mode FOUC yo'q qilindi — tema skripti `<head>`da, birinchi chizilishdan
  oldin ishlaydi
- Shrift oilalari 4 → 2 (Merriweather butunlay ishlatilmagan edi, Space Grotesk
  faqat 1 joyda); CSS ichidagi ikkilangan `@import` olib tashlandi
- htmx va nprogress `defer` bilan; nprogress CSS inline qilindi

**CSS arxitekturasi** — ildiz sabab: `--brand` tokeni bir vaqtda ham matn rangi,
ham to'q fon yuzasi sifatida ishlatilgan; dark rejimda oqqa ag'darilgani uchun
65 ta override qoidasi shu ag'darilishni orqaga qaytarish uchun yozilgan edi.

| Ko'rsatkich | Oldin | Hozir |
|---|---|---|
| `!important` | 51 | 4 (reduced-motion + print — o'rinli) |
| `body:not(.dark)` qoidalari | 35 | 0 |
| `body.dark` qoidalari | 30 | 17 |
| `.hero` ta'riflari | 5 | 1 |

**Tuzatilgan baglar**
1. Dark rejimda hero gradienti oqarib ketardi
2. Light rejimda hero sarlavhasi o'qilmasdi (global `h1` qoidasi `--ink`ni majburlardi)
3. Dark rejimda DOI raqami ko'rinmasdi (alias `var()` `:root`da hal bo'lib qolgan)
4. "Ta'lim" menyusi light rejimda umuman ko'rinmasdi (navy fonda navy matn)
5. "Ta'lim" dropdown'i klaviatura bilan ochilmasdi (`<a href="#">` edi)
6. Iqtibos tablari (APA/MLA/...) yon paneldan toshib chiqardi
7. Maqola matni qator uzunligi ~105 belgi edi (`.full-text{max-width:none}`
   `.prose` ning o'qish kengligini bekor qilgan)

**A11y** — kontrast xatolari: light 11 → 0, dark 0 → 0 (skript bilan o'lchandi).
2 ta nomsiz input `sr-only` label oldi, hamburger va til tugmalariga ARIA,
dropdown `<button>` ga o'tkazildi + `aria-expanded` sinxronlashtirildi.
Mobil 390px da gorizontal toshib ketish yo'q.

**Tipografika** — suyuq (fluid) `clamp()` shkalasi kiritildi, breakpointdagi 8 ta
takroriy `font-size` qoidasi olib tashlandi. Hero h1: 32px → 52px (1280px da).
Maqola matni: 105 → 73 belgi/qator.

### Muhit sozlamalari (2026-09-03)
- `.claude/settings.json` — model Opus 5
- `.mcp.json` — `ruflo@latest` → `ruflo@3.38.21` pin qilindi
  (`@latest` har safar tarmoqqa chiqib 30s timeout'ga sabab bo'lardi)

---

## 3. Hozirgi holat

Public frontend (bosh sahifa, maqola sahifasi, ro'yxatlar) **tayyor va
tekshirilgan** — ikkala temada, uch xil ekran o'lchamida.

**Ochiq muammolar:**

| # | Muammo | Joyi | Og'irligi |
|---|---|---|---|
| 1 | Tahririyat paneli umumiy dizayn tizimidan tashqarida | `templates/journal/dashboard/` | Yuqori |
| 2 | 14 ta test xato beradi (`django-axes`) | `journal/tests.py` | O'rta |

---

## 4. Keyingi qadamlar

### 4.1. Tahririyat panelini dizayn tizimiga ko'chirish — YUQORI

`templates/journal/dashboard/base_dashboard.html` butunlay alohida olam:
o'z HTML skeleti, `style.css` ga **umuman ulanmagan**, yana bitta Google Fonts
so'rovi, 50+ qattiq kodlangan rang (`#777`, `#333`, `#ddd`, `#f4f6f9`...),
**dark mode yo'q**. Foydalanuvchi dark rejimda panelga kirsa — oppoq sahifaga tushadi.

Ta'sirlangan fayllar (inline `style=` soni bilan):
- `dashboard/editor_article_detail.html` — 32
- `review_article.html` — 18
- `dashboard/editor_dashboard.html` — 16
- `reviewer_dashboard.html` — 14
- `dashboard/editor_make_decision.html` — 11
- `dashboard/editor_assign_reviewer.html` — 11

Reja: `base_dashboard.html` ni `style.css` ga ulash → `<style>` blokidagi
qattiq ranglarni tokenlarga almashtirish (`--surface`, `--card-border`, `--ink`,
`--muted`, `--brand`) → inline `style=` larni tozalash → ikkala temada tekshirish.

### 4.2. Test xatolarini tuzatish — O'RTA

56 testdan 14 tasi xato. 13 tasi bir sababdan:
`AxesBackendRequestParameterRequired: AxesBackend requires a request as an
argument to authenticate` — testlar `self.client.login()` chaqiradi, u esa
`request`siz `authenticate()` ga boradi.

Yechim: test uchun `AXES_ENABLED = False` qo'yish (alohida test settings yoki
`@override_settings`). Qolgan 1 tasi `ValueError`/`AttributeError` — alohida
ko'rish kerak.

**Muhim:** bu xatolar 2026-09-03 frontend ishidan OLDIN ham bor edi — o'sha
ishda faqat CSS va shablonlar o'zgartirilgan.

### 4.3. Keyinroq
- Qolgan public sahifalarni ko'zdan kechirish (`issue_detail`, `collection_*`,
  `author_detail`, `submit_article`) — refaktoringdan keyin tekshirilmagan
- `templates/journal/submit_article.html` (16KB) va `dashboard/submit_article.html`
  — ikkita o'xshash shablon, dublikat bo'lishi mumkin
- CSS minifikatsiya + `?v=NN` o'rniga `ManifestStaticFilesStorage`

---

## 5. Bilib qo'yish kerak (tuzoqlar)

Bular yo'l-yo'lakay aniqlangan — bilmasangiz vaqt yo'qotasiz.

**CSS tokenlari**
- `--brand`, `--brand-mid`, `--brand-deep`, `--on-brand` — **o'zgarmas** brand
  yuzalari. Ularni hech qachon `body.dark` da qayta e'lon qilmang: aynan shu
  xato hero'ni oqartirib yuborgan edi.
- Matn/havola uchun `--link`, `--link-strong`, `--tint` — bular ag'dariladi.
- **Alias qoidasi:** `--brand-light: var(--tint)` kabi aliaslar `var()` e'lon
  qilingan joyda hal bo'ladi. Shuning uchun ular **`:root` va `body.dark` —
  ikkalasida ham** e'lon qilingan bo'lishi shart. Faqat `:root` da qoldirsangiz,
  dark rejim qiymatini olmaydi (DOI bagi shundan chiqqan edi).

**Cache-busting** — `style.css` ni o'zgartirsangiz, `templates/base.html:40`
dagi `?v=NN` raqamini oshiring, aks holda brauzer eskisini ko'rsatadi.

**Qator oxirlari** — `templates/base.html` CRLF ishlatadi. Skript bilan tahrir
qilsangiz CRLF ni saqlang, aks holda butun fayl bo'yicha ulkan diff chiqadi.

**Dev server** — Windowsda ikkita jarayon bir portni band qila oladi
(`SO_REUSEADDR`). Shablon o'zgarishi ko'rinmayotgan bo'lsa, avval
`netstat -ano | grep <port>` bilan tekshiring: eski jarayon javob berayotgan
bo'lishi mumkin. Bu bir marta chalg'itgan.

**URL'lar** — til prefiksi bor. `curl` bilan tekshirsangiz `-L` qo'shing,
aks holda 302 olasiz.

**Kontrast o'lchash** — brauzerda `body.className` ni ish vaqtida almashtirib
o'lchash **ishonchsiz** natija beradi (ajdod ranglari qayta hal bo'lmaydi).
Har doim `localStorage.setItem('theme', ...)` + `location.reload()` bilan
toza yuklab o'lchang.

---

## 6. Bu faylni yangilash qoidasi

Har bir muhim o'zgarishdan keyin:
1. **2. Bajarilgan ishlar** — nima qilingani, aniq sana bilan
2. **3. Hozirgi holat** — hal bo'lgan muammoni o'chiring
3. **4. Keyingi qadamlar** — bajarilganini olib tashlang, yangi topilganini qo'shing
4. **5. Tuzoqlar** — vaqt yo'qotishga sabab bo'lgan har bir narsani yozing
5. Yuqoridagi **Oxirgi yangilanish** sanasini o'zgartiring

Kelajakdagi holat bu yerga yozilmaydi — faqat **haqiqatan bajarilgan** ish.
