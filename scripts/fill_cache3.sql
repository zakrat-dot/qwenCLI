INSERT INTO query_templates (relation_type, sql_template, description) VALUES 
('NOMENCLATURE_LOOKUP_VIA_TYPE', 'SELECT TOP 1 _Description FROM _Reference137 WHERE _IDRRef = %s -- check TYPE equals 0x08 first', 'Справочник Номенклатуры - проверка типа ссылки перед JOIN'),
('VT_ADDITIONAL_ATTRS', 'SELECT _Fld3060RRef, _Fld3061_TYPE FROM {ref}_VT{vt_id} WHERE {ref}_IDRRef = %s -- TYPE: 0x03=number 0x00=string 0x01=date', 'Дополнительные реквизиты контрагента - VT таблица с типами значений'),
('INVOICE_WITH_ITEMS', 'SELECT _Number, _Date_Time FROM _Document518X1 WHERE _Posted=1 AND _Marked=0 -- items from _Document518_VT16229X1', 'Счета на оплату - основной документ + табличная часть товаров/услуг'),
('COUNTERPARTY_GROUP_LOOKUP', 'SELECT TOP 1 g._Description FROM _Reference119 g WHERE g._IDRRef = c._ParentIDRRef AND g._Marked=0 -- cache by parent_id', 'Группа контрагента - родительская запись в том же справочнике, с кешированием'),
('DOC_AGGREGATION_BY_COUNTERPARTY', 'SELECT k._Description AS kontr, SUM(d._FldXXXXX) AS total FROM {doc_table} d LEFT JOIN _Reference119 k ON d._FldYYYY_RRRef = k._IDRRef WHERE d._Posted=1 GROUP BY k._Description ORDER BY total DESC', 'Агрегация по контрагенту из таблицы документа - шаблон для сводок');

INSERT INTO query_templates (relation_type, sql_template, description) VALUES 
('VT_PHONES_ADDRESSES', "SELECT _Fld3046 FROM {ref}_VT{vt_id} WHERE {ref}_IDRRef = %s AND (_Fld3046 LIKE '%+%' OR NOT)", 'Телефоны и адреса контрагента - VT таблица, фильтр по наличию + для телефонов');

INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES 
('doc_receipts_incoming', 'v1_0', '{"page":"receipts","description":"Postupleniya na raschyotny schet - dokument PostuplenieNaRaschetniySchet","source_document":"_Document478","counterparty_via":"direct field _Fld13954_RRRef to _Reference119","org_via":"direct field _Fld13947RRef to _Reference150","bank_via":"direct field _Fld13949RRef to _Reference41"}');

INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES 
('doc_expenses_outgoing', 'v1_0', '{"page":"expenses","description":"Rashody s raschyotnogo scheta - dokument SpisanieSRaschetnogoScheta","source_document":"_Document512","counterparty_via":"direct field _Fld15680_RRRef to _Reference119","org_via":"direct field _Fld15674RRef to _Reference150","bank_via":"direct field _Fld15675RRef to _Reference41"}');

INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES 
('doc_invoices_with_items', 'v1_0', '{"page":"invoices","description":"Scheta na oplatu po kupatelju s tovarami/uslugami","source_document":"_Document518X1","items_table":"_Document518_VT16229X1","counterparty_via":"separate lookup _Reference119 by kontr_ref field","org_via":"separate lookup _Reference150 by org_ref field"}');

INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES 
('counterparties_full_list', 'v1_0', '{"page":"counterparties","description":"Spravochnik kontragentov s grupami telefonami i adresami","source_table":"_Reference119","group_lookup":"parent_id self-join with cache","phones_addresses":"VT3042 tabular section filter by + for phones","additional_attrs":"VT3058 with TYPE decoding"}');

INSERT INTO query_plans_cache (plan_hash, metadata_hash, plan_json) VALUES 
('doc_aggregation_pattern', 'v1_0', '{"page":"receipts+expenses","description":"Universal template aggregation by counterparty from document table","pattern":"SELECT k._Description AS kontr SUM(d._FldXXXXX) AS total FROM {doc_table} d LEFT JOIN _Reference119 k ON d._FldYYYY_RRRef = k._IDRRef WHERE d._Posted=1 AND d._Marked=0 GROUP BY k._Description ORDER BY total DESC"}');

SELECT '=== query_templates ===' AS info;
SELECT relation_type, description FROM query_templates;
SELECT '' AS info;
SELECT '=== query_plans_cache ===' AS info;
SELECT plan_hash, SUBSTR(plan_json, 1, 80) AS preview FROM query_plans_cache;
