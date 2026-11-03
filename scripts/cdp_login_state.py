# -*- coding: utf-8 -*-
"""Определяет, залогинен ли пользователь в CDP-браузере на its.1c.ru:
ищет имя пользователя / кнопку выхода / форму логина."""
import sys
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from cdp_client import find_page_tab, CDP

tab = find_page_tab("its.1c.ru") or find_page_tab()
cdp = CDP(tab)

# Вернёмся на главную книгу
cdp.navigate("https://its.1c.ru/db/intgr83")
import time; time.sleep(3)

info = cdp.evaluate("""
(function(){
  var out = {};
  // Кнопка выхода / имя пользователя
  var logout = document.querySelector('a[href*="logout"], a[href*="exit"], .logout, [class*="user-name"], [class*="username"], .user, .account');
  out.logoutEl = logout ? (logout.textContent||'').trim().slice(0,80) + ' | href=' + (logout.href||'') : null;
  // Форма логина
  out.loginForm = !!document.querySelector('input[name="login"], input[type="password"], form[action*="login"]');
  // Ссылка "Войти"
  var loginLink = Array.from(document.querySelectorAll('a')).find(a=>/войти|вход|login/i.test(a.textContent||''));
  out.loginLink = loginLink ? loginLink.textContent.trim().slice(0,40) : null;
  // Ищем где-то в тексте упоминание логина
  var m = document.body.innerText.match(/(08576-80|Войти|Вход|Выход|Зарегистрирован)/g);
  out.hints = m ? m.slice(0,10) : [];
  return JSON.stringify(out);
})()
""")
print("Login state:", info)

# Куки сессии
cookies = cdp.get_cookies()
print("\nСессионные куки:")
for c in cookies:
    if any(k in c["name"].upper() for k in ["SESS", "LOGIN", "USER", "PROFILE", "BITRIX", "PHPSESS"]):
        print(f"  {c['name']} = {c['value'][:50]}  (domain={c.get('domain')})")

cdp.close()
