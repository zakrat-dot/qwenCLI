# qwenCLI — бэкап конфигурации Qwen Code

Резервная копия настроек, скиллов, памяти и скриптов Qwen Code.

## Структура

```
qwenCLI/
├── settings/          # settings.json (API-ключ замаскирован)
├── skills/            # 4 скилла
│   ├── 1c-book-download/
│   ├── 1c-data-model/
│   ├── duckdb-sql-memory/
│   └── excel-compare/
├── memory/
│   ├── user/          # глобальная память пользователя (C:\Users\MZ3\.qwen\memories)
│   └── project/       # память проекта c--ai-projects
└── scripts/           # Python/SQL скрипты (без __pycache__ и its_pages)
```

## ⚠️ Замаскированные секреты

Перед публикацией из файлов удалены реальные секреты (заменены на `__REDACTED__` / `__REDACTED_API_KEY__`):

| Файл | Что замаскировано |
|---|---|
| `settings/settings.json` | API-ключ `QWEN_CUSTOM_API_KEY_OPENAI_...` |
| `skills/duckdb-sql-memory/SKILL.md` | SSH-пароль `root@192.168.215.174` |
| `memory/project/docker_infrastructure.md` | SSH-пароль `root@192.168.215.174` |
| `scripts/open-webui-mssql/dab-config.json` | Пароль MSSQL (connection-string) |
| `scripts/open-webui-mssql/handle_call_tool.py` | Пароль MSSQL |
| `scripts/open-webui-mssql/mcp_1c_server.py` | Пароль MSSQL (3 места) |
| `scripts/open-webui-mssql/test_fastapi_sql.py` | Пароль MSSQL |
| `scripts/open-webui-mssql/test_sql.py` | Пароль MSSQL (2 места) |

> Внутренние IP-адреса (192.168.215.x) оставлены — это собственная инфраструктура.
> При восстановлении подставьте реальные значения вместо `__REDACTED__`.

## Исключено из бэкапа

- `scripts/__pycache__/` — скомпилированные .pyc
- `scripts/its_pages/` — дамп из 257 HTML-страниц + `_session_cookies.json` (сессионные куки Google/1C — чувствительные данные)
- Дубликаты настроек: `settings — копия.json`, `settings.json.corrupted`, `settings_Тупая_ГЕММА.json`
