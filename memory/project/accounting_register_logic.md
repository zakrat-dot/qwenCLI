---
name: Логика запросов к регистру бухгалтерии _AccRg1112
description: Как получать сальдо начало/обороты/сальдо конец из регистра бухгалтерии 1С для дашборда
type: project
---

Регистр бухгалтерии `_AccRg1112` — плоская таблица всех проводок. Каждая строка = одна проводка одного документа.

## Ключевые колонки

| Колонка | Тип | Что хранит |
|---|---|---|
| `_Period` | datetime2 | Дата документа |
| `_AccountDtRRef` | varbinary | Бинарный ID счёта по дебету |
| `_AccountCtRRef` | varbinary | Бинарный ID счёта по кредиту |
| `_Fld1116` | float | Сумма проводки |
| `_Fld1113RRef` | varbinary | ID организации (ссылка на _Reference150) |
| `_Fld1122` | nvarchar | Содержание проводки |
| `_Active` | bit | 1 = активная, 0 = сторнирована |

## Как получить сальдо начало / обороты / сальдо конец

Один SQL-запрос, `CASE WHEN` + `SUM` по 3 диапазонам дат:

```sql
SELECT организация,
  -- Сальдо на начало (все проводки ДО date_from)
  SUM(CASE WHEN _Period < date_from AND _AccountDtRRef = %s THEN _Fld1116 END) AS bal_start_dt,
  SUM(CASE WHEN _Period < date_from AND _AccountCtRRef = %s THEN _Fld1116 END) AS bal_start_ct,

  -- Обороты за период (от date_from до date_to включительно)
  SUM(CASE WHEN _Period >= date_from AND _Period < date_to+1
           AND _AccountDtRRef = %s THEN _Fld1116 END) AS turn_dt,
  SUM(CASE WHEN _Period >= date_from AND _Period < date_to+1
           AND _AccountCtRRef = %s THEN _Fld1116 END) AS turn_ct,

  -- Сальдо на конец (все проводки ДО date_to включительно)
  SUM(CASE WHEN _Period < date_to+1 AND _AccountDtRRef = %s THEN _Fld1116 END) AS bal_end_dt,
  SUM(CASE WHEN _Period < date_to+1 AND _AccountCtRRef = %s THEN _Fld1116 END) AS bal_end_ct

FROM _AccRg1112
WHERE _Active = 1
  AND (_AccountDtRRef = %s OR _AccountCtRRef = %s)
GROUP BY организация
```

## Клиентская формула (4 колонки)

```
Сальдо на начало  = bal_start_dt − bal_start_ct
Дебет (обороты)   = turn_dt
Кредит (обороты)  = turn_ct
Сальдо на конец   = bal_end_dt − bal_end_ct
```

## Почему это работает

Регистр хранит **всю историю** проводок. `CASE WHEN` фильтрует те же строки по разным диапазонам дат. Это аналог 1С-овского `Регистр.ОстаткиИОбороты(&НачПериода, &КонПериода)`.

**Проверка сходимости:** сальдо_нач + обороты_дт − обороты_кт = сальдо_кон

## Важные нюансы

- Счёт ищется в `_Acc36` по коду: `SELECT _IDRRef FROM _Acc36 WHERE _Code = '51'`
- `_IDRRef` — бинарный, передаётся в pymssql как `bytes`
- Даты в базе сдвинуты на +2000 лет (используй `shift_date()` из `core/dates.py`)
- Даты сравнивай через `CONVERT(datetime2, %s)` — pymssql может слать строки как varbinary
- Организация — `_Reference150`, соединяется через `LEFT JOIN _Reference150 o ON d._Fld1113RRef = o._IDRRef`

**Why:** Это фундаментальная логика всех страниц дашборда, работающих с регистрами бухгалтерии. Без этого каждый раз нужно заново разбирать структуру регистра.
**How to apply:** При создании любой новой страницы дашборда, которая работает со счетами (сальдо, обороты, остатки) — использовать этот шаблон запроса, меняя только HEX-ID счёта и нужные поля.
