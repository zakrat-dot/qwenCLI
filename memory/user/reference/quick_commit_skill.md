---
name: Быстрый коммит — скилл quick-commit
description: git p "сообщение" = add -A + commit + push; когда коммитить выборочно, скан секретов, стиль сообщений, известные репозитории
type: reference
---

# Скилл: quick-commit

**Файл:** `C:\Users\MZ3\.qwen\skills\quick-commit\SKILL.md`

1. **Быстрый путь**: `git p "сообщение"` — глобальный алиас = `git add -A && git commit -m "$1" && git push`
2. **Когда НЕ использовать**: чужие/нежелательные изменения в `git status` → выборочный `git add`
3. **Безопасность**: скан на секреты (API-ключи, пароли, connection-strings), мусор (`__pycache__`, `~$*`), вложенные репозитории
4. **Стиль сообщений**: короткие, по-русски, часто с датой (`архивация 23,09,26`)
5. **Конфигурация**: user.name=zakrat-dot, email=zakirov.marat@gmail.com, логин в Credential Manager zakrat-dot
6. **Репозитории**: внешний `QWEN_LOC`→duckdb_project, вложенный `qwenCLI`→qwenCLI
7. **Troubleshooting**: `rejected (fetch first)` → `git pull --rebase`; force-push только с разрешения

**Когда использовать:** пользователь просит закоммитить/сохранить работу/«скинь в гит».

**Как применять:** `git status` → скан секретов → `git p "сообщение"` → `git status` для подтверждения.
