---
name: Архитектура DashBord — модульная структура (актуально 2026-10-07)
description: Проект DashBord разбит на core/, web/, pages/ с template.html файлами, читаемыми при старте. Точка входа dashboard.py (не server.py!)
type: project
---

Проект дашборда 1С в `C:\AI_PROJECTS\Qwen_CLI\src\DashBord\site/` разбит на модули:

**Точка входа:** `dashboard.py` → ThreadingHTTPServer(8080, Handler) — НЕ server.py!
- `setup_routes()` регистрирует страницы + API маршруты через query-функции
- Старый монолитный `server.py` (1474 строки) больше не используется

**config.py:** DB_CONFIG (pymssql → BP_MAIN_COPY), DATE_SHIFT=2000, PORT=8080

**core/** — базовый слой:
- `db.py` — `get_connection()` → pymssql.connect(**DB_CONFIG)
- `dates.py` — `shift_date()` (+2000 лет), `unshift_date()` (-2000 лет)
- `router.py` — `Handler(SimpleHTTPRequestHandler)` с маршрутизацией PAGES и API_ROUTES
- `middleware.py` — `@api_endpoint` декоратор (парсинг params, валидация, try/except)

**web/** — шаблонизация:
- `common_css.py` — COMMON_CSS строка (общие стили)
- `layout.py` — `build_page(title, body, css_extra='')` → полный HTML

**pages/__init__.py:** PAGES list + регистрация всех страниц через PAGE dict'ы из подпапок

**pages/** — 5 страниц, каждая в своей папке:
1. `invoices/` — Счета на оплату покупателю (_Document518X1)
2. `receipts/` — Поступления на расчётный счёт (_Document478)
3. `expenses/` — Расходы с расчётного счёта (_Document512)
4. `account51/` — Счёт 51 регистр бухгалтерии (_AccRg1112)
5. `counterparties/` — Контрагенты и их данные

Каждая страница: `__init__.py` (PAGE dict), `template.html` (файл на диске, читается один раз при старте сервера через Path.read_text()), `query.py` (SQL функция)

**Ключевые правила:**
- HTML inline (не отдельные HTTP-ресурсы для CSS/JS)
- Роуты регистрируются автоматически через PAGES list в pages/__init__.py + API_ROUTES в dashboard.py setup_routes()
- Навигация: Счета · Поступления · Расходы · Счёт 51

**Why:** Один файл server.py (1474 строки) стал нерулируемым. Разбивка упрощает добавление новых страниц и запросов.

**How to apply:** Новые страницы = новая папка в `pages/` с `__init__.py`, `template.html`, `query.py`. Не трогать core/ и web/.
