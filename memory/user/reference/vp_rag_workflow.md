---
name: Visual Paradigm .vpp → MD + RAG-чанки (workflow)
description: Как вытаскивать структуру UML из .vpp (SQLite) в MD и плоские RAG-чанки — готовый проект VP_RAG, скрипт vp_to_rag.py, формат чанков, статус
type: reference
---

## Что это

Повторяющаяся операция пользователя: выгрузка проектов Visual Paradigm (`.vpp`) в:
1. **Структурированный Markdown** (по диаграммам + дерево пакетов) — для человека
2. **Плоские RAG-чанки (JSON)** с якорями — для индексации (эмбеддинги)

## Где лежит проект (единое место)

`C:\AI_PROJECTS\QWEN_LOC\VP_RAG\`
- `README.md` — полная документация (формат, статус, как запускать)
- `vp_to_rag.py` — основной скрипт выгрузки
- `vp_show_chunks.py` — проверка образцов чанков
- `out\` — результаты: `{проект}_структура.md` + `{проект}_rag_chunks.json`

## Как запустить

```
py -3 C:\AI_PROJECTS\QWEN_LOC\VP_RAG\vp_to_rag.py <путь_к_.vpp> [папка_выхода]
```
Без аргументов — elko (копия в Documents), выход в `VP_RAG\out`.
Проверка: `py -3 VP_RAG\vp_show_chunks.py <путь_к_rag_chunks.json>`.

## Ключевые факты о формате .vpp (чтобы не переоткрывать)

- `.vpp` = **SQLite** (не ZIP/XML). Таблицы: `MODEL_ELEMENT`, `DIAGRAM`, `DIAGRAM_ELEMENT`.
- `MODEL_ELEMENT`: ID, USER_ID, MODEL_TYPE, PARENT_ID, NAME, DEFINITION (blob).
- **USER_ID есть ТОЛЬКО у UseCase** (UC01, UC02, …) — это якорь для поиска элемента в Visual Paradigm. У NOTE/диаграмм USER_ID=NULL, якорь = SQLite ID.
- **Читаемый текст** (описание UseCase, текст NOTE) — в `DEFINITION` в поле `documentation_plain="..."`. НЕ в NAME, НЕ извлекать «чистый текст» из сериализации — там мусор.
- **Концы ассоциаций** — составные ссылки `<контейнер>:<элемент>` (Subsystem:UseCase, Package:UseCase); реальный элемент = часть после последнего `:`. Без этого теряется ~50% связей.
- **NAME может содержать не-UTF-8 байты** → читать через `CAST(NAME AS BLOB)` + decode `errors="replace"`. Иначе sqlite3 падает с OperationalError.
- Python: `py -3` (`python` не в PATH). CLI sqlite3 на машине нет. Мульти-строки в `py -c` в cmd.exe не работают — писать .py файлы.

## Формат RAG-чанка

```json
{"project": "...", "kind": "usecase|note|diagram", "id": "<SQLite ID>",
 "user_id": "UC04|null", "name": "...", "diagrams": ["..."],
 "package_path": "Пакет > Подпакет", "connections": {"to": [], "include": [], "extend": []},
 "text": "готовый текст для эмбеддинга"}
```

## Статус (2026-10-23)

Выгружено 5 проектов — **6437 чанков** (elko 2314, Майтек 3282, MitecClients 250, AI 252, Дашборд и AI 339).
**НЕ сделано:** эмбеддинги (nomic-embed-text), векторная база, скрипт поиска/запросов.
Следующий шаг (по запросу пользователя): JSON-чанки → nomic-embed-text → векторное хранилище → RAG-запросы.

**Why:** Пользователь (2026-10-23) попросил запомнить workflow как повторяющуюся операцию и оформить как проект, чтобы при вопросе сразу было понятно что делать.

**How to apply:** При упоминании «выгрузить .vpp», «RAG по диаграммам», «новый проект Paradigm» — не писать скрипт с нуля, а запустить `VP_RAG\vp_to_rag.py`. Новые .vpp искать по корню `C:\Users\MZ3\AppData\Roaming\VisualParadigm\` (список динамический, см. `visual_paradigm_projects.md`).
