# -*- coding: utf-8 -*-
"""Проверяет, есть ли в CDP-профиле сессия логина на its.1c.ru."""
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from cdp_client import find_page_tab, CDP

tab = find_page_tab("its.1c.ru") or find_page_tab()
if not tab:
    print("Не найдена вкладка page")
    sys.exit(1)

cdp = CDP(tab)
print("URL:", tab.get("url"))
print("TITLE:", cdp.evaluate("document.title"))

cookies = cdp.get_cookies()
print("\n=== Куки 1c.ru ===")
for c in cookies:
    dom = c.get("domain", "")
    if "1c.ru" in dom:
        print(f"  {c['name']} = {c['value'][:40]}  (domain={dom})")

# Есть ли форма логина на странице?
has_login_form = cdp.evaluate(
    "!!(document.querySelector('input[name=login]') || "
    "document.querySelector('form[action*=\"login\"]') || "
    "document.querySelector('.login-form') || "
    "document.querySelector('[class*=login]'))"
)
print("\nФорма логина на странице:", has_login_form)

# Есть ли iframe с контентом книги?
iframe = cdp.evaluate(
    "(function(){var f=document.querySelector('iframe#w_metadata_doc_frame');"
    "if(!f) return 'NO_IFRAME';"
    "if(f.getAttribute('srcdoc')) return 'SRCDOC len='+f.getAttribute('srcdoc').length;"
    "return 'SRC='+f.getAttribute('src');})()"
)
print("iframe w_metadata_doc_frame:", iframe)

cdp.close()
