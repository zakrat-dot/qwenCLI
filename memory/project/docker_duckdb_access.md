---
name: Прямой доступ к DuckDB через Docker exec
description: Контейнер duckdb_ai_core содержит 3 базы DuckDB (semantic_core, meta_schema, BP_MAIN_COPY). Доступ через docker exec команды для быстрых запросов метаданным 1С
type: project
---

# Прямой доступ к DuckDB базам через Docker контейнер

**Контейнер:** `duckdb_ai_core` (ID: 2fddc646f389)  
**Путь к базам:** `/app/data/` внутри контейнера

## Три базы данных

### semantic_core.duckdb (~29MB, 27 таблиц)
Семантическое ядро — граф связей метаданных 1С:
- **graph_nodes_legacy** (6664 узла) — объекты 1С с колонками: node_id, object_uid, sql_table, object_kind, object_name, parent_node_id, schema_name, suffix_extension
- **field_registry** (61053 поля) — все поля объектов: field_id, node_dec_id, table_part_dec_id, field_name, business_name, sql_base, storage_type, primitive_type, cardinality, target_dec_id
- **graph_edges_legacy** (~10k рёбер) — связи между узлами через поля: edge_id, from_node_id, to_node_id, relation_type, cardinality
- **edge_targets_legacy** (26173 записей) — целевые связи полей: from_node_dec_id → to_node_dec_id с field_name и business_name. Типы связей: "belongs_to", "has_parent"
- **object_registry** (6664 записи) — дубль graph_nodes_legacy в формате hex_id/dec_id/class/sql_table/suffix_extension/parent_dec_id
- **relations** (9099 записей) — семантические связи между концептами: source_concept → target_concept с relation_type и description

### meta_schema.duckdb (~20MB, 4 таблицы)
Метаданные схемы 1С в компактном формате:
- **meta_nodes** (6664 узла) — dec_id, hex_id, object_name, object_path, class, synonym, parent_dec_id, suffix_extension, created_at
- **meta_fields** (61053 поля) — field_id, node_id, vt_parent_id, field_sql_name, field_name, business_name, synonym, storage_type, primitive_type, cardinality, target_dec_id, created_at

### BP_MAIN_COPY.duckdb (~16MB)
Копия производственной БД 1С (бухгалтерия). Содержит таблицы _AccRg1112 и другие регистры.

## Команды docker exec для запросов

```bash
# Список таблиц
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c ".tables"

# Структура таблицы
docker exec duckdb_ai_core duckdb /app/data/meta_schema.duckdb -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'meta_nodes' ORDER BY ordinal_position;"

# Запрос к данным
docker exec duckdb_ai_core duckdb /app/data/semantic_core.duckdb -c "SELECT object_name, sql_table FROM graph_nodes_legacy LIMIT 10;"
```

## Ключевые выводы для DashBord
- meta_schema и semantic_core содержат одни и те же данные (6664 объекта, 61053 поля), но в разных форматах
- edge_targets_legacy — главный справочник связей "поле X объекта A указывает на объект B"
- Docker exec даёт мгновенный доступ к метаданным без Python/pymssql

**Why:** DashBord строит запросы к MSSQL базе 1С, но структура таблиц и полей хранится в DuckDB. Прямой docker exec позволяет быстро исследовать связи между объектами без запуска Python скриптов.
**How to apply:** При разработке страниц дашборда сначала проверяй структуру метаданных через docker exec, затем пиши SQL запросы к BP_MAIN_COPY через pymssql.
