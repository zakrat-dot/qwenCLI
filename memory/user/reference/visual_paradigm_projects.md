---
name: Visual Paradigm .vpp проекты — расположение
description: Где лежат все .vpp файлы Visual Paradigm (UML 2.0) пользователя; формат = SQLite, не ZIP/XML; список ДИНАМИЧЕСКИЙ — появляются новые
type: reference
---

## Где лежат .vpp файлы Visual Paradigm

**ГЛАВНАЯ (корневая) папка:** `C:\Users\MZ3\AppData\Roaming\VisualParadigm\`
Структура: `<workspace>\teamwork_client\projects\<имя_проекта>\<имя_проекта>.vpp`
Рабочие области (workspaces): `dashbord`, `ws`, `ws1` (и могут появиться новые).

**ВАЖНО (2026-10-23): список проектов ДИНАМИЧЕСКИЙ — пользователь добавляет новые .vpp.**
Не полагаться на список ниже как на полный. Перед работой искать актуальный список:
```
dir /s /b "C:\Users\MZ3\AppData\Roaming\VisualParadigm\*.vpp"
```
(или glob `**\*.vpp`), отфильтровать системные файлы (см. ниже).

### Известные проекты (на 2026-10-23, 6)
| Проект | Путь | Размер |
|---|---|---|
| elko | `ws1\teamwork_client\projects\elko\elko.vpp` | 29 МБ |
| Майтек | `ws\teamwork_client\projects\Майтек\Майтек.vpp` | 58 МБ |
| MitecClients | `ws\teamwork_client\projects\MitecClients\MitecClients.vpp` | 4.6 МБ |
| AI | `ws\teamwork_client\projects\AI\AI.vpp` | 3.3 МБ |
| Дашборд и AI | `dashbord\teamwork_client\projects\Дашборд и AI\Дашборд и AI.vpp` | 3.7 МБ |
| Дашборд и AI (копия) | `ws\teamwork_client\projects\Дашборд и AI\Дашборд и AI.vpp` | 3.7 МБ |

### Игнорировать (не проекты)
- `*.vpprefdata\.systemproject.vpp` — системные файлы VP
- `workingcopies\*.vpp_work_*_trunk` — временные рабочие копии

### Копия в Documents
`C:\Users\MZ3\Documents\VPProjects\elkomp28-07-25.vpp` = байт-в-байт копия `elko.vpp` (29 341 696 байт).

## Формат файла (КРИТИЧНО для RAG/чтения)
`.vpp` — это **SQLite-база** (сигнатура `SQLite format 3`), НЕ ZIP и НЕ XML. Читаем напрямую через `sqlite3` (Python `py -3`, CLI sqlite3 на машине НЕТ).

### Таблицы (на примере elko)
- `MODEL_ELEMENT` (5241) — UML-элементы: ID, USER_ID, USER_ID_PARENT, MODEL_TYPE, PARENT_ID, NAME, DEFINITION(blob)
- `DIAGRAM_ELEMENT` (4051) — фигуры: SHAPE_TYPE, DIAGRAM_ID, MODEL_ELEMENT_ID, DEFINITION
- `DIAGRAM` (128) — DIAGRAM_TYPE, PARENT_MODEL_ID, NAME, DEFINITION
- `PROJECT_FILE` (210), `PROJECT_INFO` (1), `TW_HISTORY`, `USER_ID_FORMAT`

### Типы диаграмм (elko)
UseCaseDiagram 106 · ActivityDiagram 13 · ReportDiagram 6 · UseCaseDescriptionDiagram 2 · ERDiagram 1

### Типы элементов (elko, топ)
UseCase 1879 · Association 1133 · NOTE 307 · ActivityAction 214 · ControlFlow 214 · Include 86 · Package 79 · Activity 41

### Как читать (рабочий шаблон)
```
py -3 -c "import sqlite3; con=sqlite3.connect(r'ПУТЬ\к\elko.vpp'); cur=con.cursor(); [print(r) for r in cur.execute('SELECT DIAGRAM_TYPE, NAME FROM DIAGRAM ORDER BY 1,2')]"
```
- Читаемый текст: колонки `NAME`, `MODEL_TYPE`, `DIAGRAM_TYPE`, `SHAPE_TYPE`.
- `DEFINITION` (blob) = бинарный хедер + читаемый текст (сериализованные свойства: pmAuthor, pmCreateDateTime, имена). Текстовую часть можно извлечь.
- Иерархия модели: `PARENT_ID` / `USER_ID_PARENT` (дерево: пакет → use case → include).

**Why:** Пользователь (2026-10-23) попросил найти все .vpp и запомнить расположение для RAG-индексации UML-моделей. Файл elko уже исследован — это UML 2.0 модель розничной/кассовой системы ELKOM (106 use case диаграмм: инвентаризация, бонусы, обмен БК–ЦБ, дашборды, прослеживаемость, PUSH/Telegram).

**How to apply:** При упоминании Visual Paradigm / .vpp / UML-моделей / RAG по диаграммам — брать файлы из этих путей, читать как SQLite через `py -3`, не пытаться распаковывать как ZIP и не выгружать в XML. Готовый workflow выгрузки — проект `C:\AI_PROJECTS\QWEN_LOC\VP_RAG\` (см. память `vp_rag_workflow.md`).
