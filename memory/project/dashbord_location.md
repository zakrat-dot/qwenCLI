---
name: Проект DashBord в C:\AI_PROJECTS\Qwen_CLI\src\DashBord
description: Исходники дашборда 1С, server.py, файлы контекста и документации расположены в папке DashBord
type: project
---

Проект дашборда для 1С:Enterprise находится в `C:\AI_PROJECTS\Qwen_CLI\src\DashBord`.

- **server.py** — `site/server.py` (порт 8080, pymssql → BP_MAIN_COPY)
- **Контекст и документация** — `symantic_core.md` (формальная модель 1С в DuckDB), `accounting_registers.md` (справочник по регистрам бухгалтерии)
- **venv** — `site/venv/`

**Why:** Пользователь указал, что все файлы проекта DashBord должны сохраняться в эту папку, а не разбрасываться по другим директориям.

**How to apply:** При создании новых файлов, скриптов, документации по дашборду — сохранять в `C:\AI_PROJECTS\Qwen_CLI\src\DashBord\` или его подпапки.
