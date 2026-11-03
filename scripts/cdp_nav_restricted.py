# -*- coding: utf-8 -*-
"""Навигирует САМ БРАУЗЕР (CDP) на заблокированную страницу и смотрит,
что реально отрендерилось. Это ground truth: если браузер видит контент —
значит сессия валидна и контент можно вытаскивать через CDP."""
import sys
import time
sys.path.insert(0, r"C:\AI_PROJECTS\QWEN_LOC\scripts")
from cdp_client import find_page_tab, CDP

tab = find_page_tab("its.1c.ru") or find_page_tab()
cdp = CDP(tab)

url = "https://its.1c.ru/db/intgr83/content/93/hdoc"
print("Навигация:", url)
cdp.navigate(url)
time.sleep(4)

print("URL после:", cdp.evaluate("location.href"))
print("TITLE:", cdp.evaluate("document.title"))

# Что в iframe?
info = cdp.evaluate("""
(function(){
  var f = document.querySelector('iframe#w_metadata_doc_frame');
  if(!f) return 'NO_IFRAME';
  var out = {};
  out.srcdoc = f.getAttribute('srcdoc') ? f.getAttribute('srcdoc').length : null;
  out.src = f.getAttribute('src');
  // Если src — пробуем прочитать содержимое iframe (same-origin)
  try {
    var d = f.contentDocument;
    if(d && d.body){
      out.bodyTextLen = d.body.innerText.length;
      out.bodyTextHead = d.body.innerText.slice(0,300);
    } else {
      out.bodyTextLen = 'NO_ACCESS';
    }
  } catch(e){ out.err = String(e); }
  return JSON.stringify(out);
})()
""")
print("iframe info:", info)

# Общий текст страницы
bodytext = cdp.evaluate("document.body ? document.body.innerText.slice(0,400) : 'NO_BODY'")
print("\nbody text (400):", bodytext)

cdp.close()
