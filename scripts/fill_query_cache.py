import duckdb
conn = duckdb.connect(r"C:\AI_PROJECTS\Base_DuckDb\src\semantic_core.duckdb")

# Заполняем query_plans_cache реальными планами запросов из DashBord
plans = [
    {
        "plan_hash": "accrg1112_dt51_ct62_counterparty",
        "metadata_hash": "v1_0",
        "plan_json": '{"page":"payment_receipts","description":"Поступления оплаты Дт51 Кт62 по контрагентам","source_register":"_AccRg1112","counterparty_via":"subkonto Ct1 (_ValueCt1_RRef → _Reference119)","org_via":"direct field (_Fld1113RRef → _Reference150)","accounts":{"debit":"51 (Расчётные счета)","credit":"62.xx (покупатели)"},"sql_template":"SELECT c._Description, o._Description, SUM(d._Fld1116), MAX(d._Period), COUNT(*) FROM _AccRg1112 d LEFT JOIN _Reference150 o ON d._Fld1113RRef = o._IDRRef LEFT JOIN _Reference119 c ON d._ValueCt1_RRRef = c._IDRRef WHERE d._Active=1 AND d._Period >= ? AND d._AccountDtRRef = {acc51_idrref} AND d._AccountCtRRef IN ({acc62_list}) GROUP BY c._Description, o._Description"}'
    },
    {
        "plan_hash": "account51_balance_turnover",
        "metadata_hash": "v1_0",
        "plan_json": '{"page":"account51","description":"Сальдо/обороты счёта 51 по организациям","source_register":"_AccRg1112","org_via":"direct field (_Fld1113RRef → _Reference150)","accounts":{"target":"51 (Расчётные счета)"},"sql_template":"SELECT o._Description, SUM(CASE WHEN d._Period < date_from AND d._AccountDtRRef = acc_id THEN d._Fld1116 ELSE 0 END) AS bal_start_dt, SUM(CASE WHEN d._Period >= date_from AND d._Period <= date_to AND d._AccountCtRRef = acc_id THEN d._Fld1116 ELSE 0 END) AS turn_ct FROM _AccRg1112 d LEFT JOIN _Reference150 o ON d._Fld1113RRef = o._IDRRef WHERE d._Active=1 GROUP BY o._Description"}'
    },
    {
        "plan_hash": "document_counterparty_expense",
        "metadata_hash": "v1_0",
        "plan_json": '{"page":"expenses","description":"Расходы — контрагент из таблицы документа (прямое поле)","source_document":"_Document512","counterparty_via":"direct field (_FldXXXXX_RRRef → _Reference119)","sql_template":"SELECT k._Description, SUM(d._Fld15682) FROM _Document512 d LEFT JOIN _Reference119 k ON d._Fld15680_RRRef = k._IDRRef WHERE d._Posted=1 AND d._Marked=0 GROUP BY k._Description"}'
    },
]

for p in plans:
    conn.execute("""INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES (?, ?, ?);""", [p["plan_hash"], p["metadata_hash"], p["plan_json"]])

print("Вставлено планов:", len(plans))

# Показать результат — шаблоны
print("\n=== query_templates ===")
for row in conn.execute("SELECT relation_type, description FROM query_templates;").fetchall():
    print(f"  {row[0]:25s} → {row[1]}")

# Показать результат — планы запросов
print("\n=== query_plans_cache ===")
import json
for phash, mhash, pjson in conn.execute("SELECT plan_hash, metadata_hash, plan_json FROM query_plans_cache;").fetchall():
    pj = json.loads(pjson)
    print(f"  {phash}")
    print(f"    описание: {pj['description']}")

conn.close()

