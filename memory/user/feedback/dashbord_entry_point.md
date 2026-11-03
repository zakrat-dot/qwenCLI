---
name: DashBord — точка входа dashboard.py, не server.py!
description: Критическое правило: при работе с проектом DashBord использовать dashboard.py как точку входа. server.py — старая версия, больше НЕ используется.
type: feedback
---

## Факт (подтверждено пользователем 2026-10-07)

**Точка входа проекта DashBord:** `dashboard.py` в папке `C:\AI_PROJECTS\Qwen_CLI\src\DashBord\site/`
- ThreadingHTTPServer на порту 8080, маршрутизация через setup_routes()
- Роуты регистрируются автоматически: PAGES list + API_ROUTES

**server.py — СТАРАЯ версия!** Монолитный файл (1474 строки) больше не используется. Никогда НЕ править server.py для DashBord!

## Почему: Пользователь жёстко указал на ошибку. Работа со старым файлом приводит к потере времени и неправильным изменениям.

## Как применять: При ЛЮБОЙ работе с проектом DashBord — всегда использовать dashboard.py, pages/, core/, web/. Никогда не трогать server.py!
