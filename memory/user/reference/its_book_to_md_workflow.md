---
name: 1C ITS книга → Markdown (workflow)
description: Как скачивать полный текст книги с its.1c.ru (CDP-профиль + requests + warm-up) и конвертировать в чистый Markdown
type: reference
---

**ГЛАВНЫЙ СПОСОБ (2026-10-29):** skill `1c-book-download` + мастер-скрипт
`C:\AI_PROJECTS\QWEN_LOC\scripts\its_book.py` — одной командой скачивает ЛЮБУЮ
книгу с its.1c.ru в Markdown для Obsidian (warm-up → страницы → MD → картинки →
TOC → переименование → копирование). Запуск:
`python its_book.py --book <ID> --output "C:\Voult\Volt\1c\Книги1сИтс\<Название>" --title "..."`.
Подробности — в `C:\Users\MZ3\.qwen\skills\1c-book-download\SKILL.md`.
Ниже — детали пайплайна и ключевые моменты (warm-up, картинки из `<base>`).

Повторяемый workflow выгрузки книги с портала 1C ITS (its.1c.ru) в Markdown.

**Ключевой момент — warm-up сессии.** Куки логина (BITRIX_SM_LOGIN, PHPSESSID) сами по себе дают 401 «Доступ к данному материалу ограничен» на контентных страницах. Нужно сначала сделать GET главной страницы книги (`https://its.1c.ru/db/<book>`), после чего ВСЕ страницы (включая ранее «restricted») становятся доступны через requests. Кука USER_TYPE меняется после warm-up.

**Пайплайн (реализован в `C:\AI_PROJECTS\QWEN_LOC\scripts\`):**
1. `cdp_client.py` — минимальный CDP-клиент (websocket, localhost:9222).
2. Chrome с профилем `C:\ChromeCDP` (как для DeepSeek) — пользователь уже залогинен.
3. `cdp_contrast.py` — warm-up + проверка доступности страниц.
4. `its_download.py` — скачивает ВСЕ страницы: куки из `_session_cookies.json`, warm-up, пейсинг 0.8–1.6с, 3 ретрая, resume. Контент — из `iframe#w_metadata_doc_frame` (атрибут `srcdoc` или `src`). Сохраняет `raw/NNN.html` + `_download_summary.json`.
5. `its_convert.py` — HTML→MD. Понимает классы 1C ITS: `MsoNormal`, `command`/`interface` (инлайн-код), `bold`, `listingnazv` (подпись листинга), `codebox`+`codeline[N]indent` (блок кода, отступ 4 пробела/уровень), `vrezkanazv`/`vrezkabody` (блок «Подробнее»), `picyakor`+`img` (рисунок), `picnazv` (подпись рисунка).
6. `its_toc.py` — оглавление TOC.md из `_id2title.json`, группировка по «Глава N».
7. `its_rename.py` — переименовывает `NNN.md` → `NNN. <Заголовок>.md` в папке Obsidian (номер-префикс сохраняет порядок и уникальность при повторяющихся заголовках, напр. «Общая информация» на 8 стр.) и пересобирает TOC.md со ссылками на новые имена. Заголовки берутся из `_id2title.json`; запрещённые символы Windows санитизируются.
8. `its_download_images.py` — скачивает ВСЕ картинки в `images/` рядом с md и подменяет ссылки `![image](<файл>?_=...)` → `![image](images/<файл>)`.

**КАРТИНКИ — КЛЮЧЕВОЙ МОМЕНТ (самое трудное).** В srcdoc картинки имеют ОТСОСИТЕЛЬНЫЙ src вида `01_02.png?_=0000153266FEEB6F-v2` (имя + cache-buster токен `?_=...`). Гадать URL бесполезно — все «очевидные» паттерны (`/db/intgr83/content/{pid}/hdoc/<файл>`, `/db/intgr83/<файл>`, `/files/`, `/images/`) дают 404. **Правильный базовый URL берётся из тега `<base>` в HTML страницы:** `<base id="w_base" href="/db/content/intgr83/src/13.html">`. Директория `/db/content/intgr83/src/` ОДИНАКОВА на всех страницах (имя файла в base меняется — cover.html/46.html/96.html… — но каталог тот же). Итоговый URL картинки: `https://its.1c.ru/db/content/intgr83/src/<файл>?_=<токен>`. Токен можно брать из src, но работает и без него. Для другой книги паттерн тот же: `/db/content/<book>/src/<файл>`. Проверено: 160 картинок (159 PNG + 1 JPG-обложка) скачано, 0 ошибок, 0 битых ссылок в md.

**БЫВАВШИЙ БАГ (исправлен):** подписи листинга/рисунков с вложенными `<span class=bold>` давали сломанный MD (`****Листинг****1.****56.**`). Фикс: для `listingnazv`/`picnazv` использовать `el.get_text()` (а не `inline_children()`), т.к. они целиком жирные.

**Python:** `C:\Users\MZ3\AppData\Local\Programs\Python\Python311\python.exe` (НЕ в PATH).

**ФИНАЛЬНОЕ МЕСТО md — Obsidian-vault.** Готовые md-файлы + TOC.md переносятся (Move-Item) в `C:\Voult\Volt\1c\Книги1сИтс\<название книги>\` (папку создать, если нет). Рабочие файлы (raw/, скрипты, json) остаются в `scripts/its_pages/`.

**Пример результата (книга intgr83, 257 стр.):**
- Рабочие: `scripts/its_pages/` → `raw/` (257 html), `_id2title.json`, `_download_summary.json`.
- Финал (Obsidian): `C:\Voult\Volt\1c\Книги1сИтс\Технологии интеграции\` → 257 md (имена `NNN. <Заголовок>.md`) + TOC.md со ссылками на эти имена (~1.4 МБ).
