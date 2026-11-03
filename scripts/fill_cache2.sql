INSERT INTO query_templates (relation_type, sql_template, description) VALUES 
('DOC_INCOMING_PAYMENT', 'SELECT d._Number, d._Date_Time, k._Description FROM _Document478 d LEFT JOIN _Reference119 k ON d._Fld13954_RRRef = k._IDRRef WHERE d._Posted=1 AND d._Marked=0', 'Поступления — документ ПоступлениеНаРасчетныйСчёт, контрагент прямым полем'),
('DOC_OUTGOING_PAYMENT', 'SELECT d._Number, d._Date_Time, k._Description FROM _Document512 d LEFT JOIN _Reference119 k ON d._Fld15680_RRRef = k._IDRRef WHERE d._Posted=1 AND d._Marked=0', 'Расходы — документ СписаниеСРасчетногоСчета, контрагент прямым полем'),
('DOC_BANK_JOIN_ORG_KONTR_BNK', 'LEFT JOIN _Reference150 o ON doc._FldXXXXX_RRRef = o._IDRRef LEFT JOIN _Reference119 k ON doc._FldYYYYY_RRRef = k._IDRRef LEFT JOIN _Reference41 b ON doc._FldZZZZZ_RRRef = b._IDRRef', 'Стандартный набор: Организация + Контрагент + Банк через прямые поля документа'),
('VT_TABULAR_JOIN', 'SELECT * FROM {doc_table}_VT{vt_id} WHERE {doc_table}_IDRRef = %s ORDER BY _LineNo{id}', 'Табличная часть — JOIN по родительскому IDRRef, сортировка по номеру строки');

INSERT INTO query_templates (relation_type, sql_template, description) VALUES 
('NOMENCLATURE_LOOKUP_VIA_TYPE', 'SELECT TOP 1 _Description FROM _Reference137 WHERE _IDRRef = %s -- check TYPE=0x08 first', 'Справочник Номенклатуры — проверка типа ссылки перед JOIN'),
('VT_ADDITIONAL_ATTRS', 'SELECT _Fld3060RRef, _Fld3061_TYPE FROM {ref}_VT{vt_id} WHERE {ref}_IDRRef = %s -- TYPE: 0x03=number 0x00=string 0x01=date', 'Дополнительные реквизиты контрагента — VT таблица с типами значений'),
('VT_PHONES_ADDRESSES', "SELECT _Fld3046 FROM {ref}_VT{vt_id} WHERE {ref}_IDRRef = %s AND (_Fld3046 LIKE '%+%' OR NOT)", 'Телефоны и адреса контрагента — VT таблица, фильтр по наличию + для телефонов'),
('INVOICE_WITH_ITEMS', 'SELECT _Number, _Date_Time FROM _Document518X1 WHERE _Posted=1 AND _Marked=0 -- items from _Document518_VT16229X1', 'Счета на оплату — основной документ + табличная часть товаров/услуг'),
('COUNTERPARTY_GROUP_LOOKUP', 'SELECT TOP 1 g._Description FROM _Reference119 g WHERE g._IDRRef = c._ParentIDRRef AND g._Marked=0 -- cache by parent_id', 'Группа контрагента — родительская запись в том же справочнике, с кешированием'),
('DOC_AGGREGATION_BY_COUNTERPARTY', 'SELECT k._Description AS kontr, SUM(d._FldXXXXX) AS total FROM {doc_table} d LEFT JOIN _Reference119 k ON d._FldYYYY_RRRef = k._IDRRef WHERE d._Posted=1 GROUP BY k._Description ORDER BY total DESC', 'Агрегация по контрагенту из таблицы документа — шаблон для сводок');

INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES 
('doc_receipts_incoming', 'v1_0', '{"page":"receipts","description":"Поступления на расчётный счёт - документ ПоступлениеНаРасчетныйСчет","source_document":"_Document478","counterparty_via":"direct field _Fld13954_RRRef to _Reference119","org_via":"direct field _Fld13947RRef to _Reference150","bank_via":"direct field _Fld13949RRef to _Reference41","filters":{"posted":true,"marked":false},"sort_options":["date","kontr","amount"]},
('doc_expenses_outgoing', 'v1_0', '{"page":"expenses","description":"Расходы с расчётного счёта - документ СписаниеСРасчетногоСчета","source_document":"_Document512","counterparty_via":"direct field _Fld15680_RRRef to _Reference119","org_via":"direct field _Fld15674RRef to _Reference150","bank_via":"direct field _Fld15675RRef to _Reference41","filters":{"posted":true,"marked":false},"sort_options":["date","kontr","amount"]},
('doc_invoices_with_items', 'v1_0', '{"page":"invoices","description":"Счета на оплату покупателю с товарами/услугами","source_document":"_Document518X1","items_table":"_Document518_VT16229X1","counterparty_via":"separate lookup _Reference119 by kontr_ref field","org_via":"separate lookup _Reference150 by org_ref field","nomenclature_lookup":"TYPE=0x08 check then JOIN to _Reference137"},
('counterparties_full_list', 'v1_0', '{"page":"counterparties","description":"Справочник контрагентов с группами, телефонами и адресами","source_table":"_Reference119","group_lookup":"parent_id self-join with cache","phones_addresses":"VT3042 tabular section filter by + for phones","additional_attrs":"VT3058 with TYPE decoding 0x03=number 0x00=string 0x01=date"},
('doc_aggregation_pattern', 'v1_0', '{"page":"receipts+expenses","description":"Универсальный шаблон агрегации по контрагенту из таблицы документа","pattern":"SELECT k._Description AS kontr, SUM(d._FldXXXXX) AS total FROM {doc_table} d LEFT JOIN _Reference119 k ON d._FldYYYY_RRRef = k._IDRRef WHERE d._Posted=1 AND d._Marked=0 GROUP BY k._Description ORDER BY total DESC"}');

SELECT '=== query_templates ===' AS info;
SELECT relation_type, description FROM query_templates;
SELECT '' AS info;
SELECT '=== query_plans_cache ===' AS info;
SELECT plan_hash, SUBSTR(plan_json, 1, 80) AS preview FROM query_plans_cache;
