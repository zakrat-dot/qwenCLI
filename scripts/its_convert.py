# -*- coding: utf-8 -*-
"""Конвертер HTML-страниц книги intgr83 в чистый Markdown.
Понимает структуру 1C ITS:
  <h5> — заголовок страницы
  <p class="MsoNormal"> — абзац
  <span class="command|interface"> — инлайн-код
  <span class="bold"> — жирный
  <p class="listingnazv"> — подпись листинга
  <div class="codebox"> + <p class="codeline[N]indent|textline"> — блок кода
  <p class="vrezkanazv|vrezkabody"> — блок «Подробнее»
  <p class="picyakor"> + <img> — рисунок
  <p class="picnazv"> — подпись рисунка
  <A href> — внутренние/внешние ссылки
"""
import json
import os
import re
import sys
from bs4 import BeautifulSoup, NavigableString

BASE = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages"
RAW = os.path.join(BASE, "raw")
MD = os.path.join(BASE, "md")
os.makedirs(MD, exist_ok=True)

INDENT = "    "  # 4 пробела на уровень отступа кода

def inline_md(node):
    """Рекурсивно конвертирует инлайн-содержимое в Markdown-текст."""
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", str(node))
    name = node.name
    if name in ("script", "style"):
        return ""
    if name == "br":
        return "  \n"
    if name == "img":
        src = node.get("src", "")
        alt = node.get("alt", "image")
        return f"![{alt}]({src})"
    if name == "a":
        href = node.get("href", "")
        text = inline_children(node).strip()
        if not text:
            return ""
        return f"[{text}]({href})"
    cls = " ".join(node.get("class", []))
    inner = inline_children(node)
    if "command" in cls or "interface" in cls:
        return f"`{inner.strip()}`"
    if "bold" in cls:
        return f"**{inner.strip()}**"
    if "italic" in cls or "ancopy" in cls:
        return f"*{inner.strip()}*"
    return inner

def inline_children(el):
    return "".join(inline_md(c) for c in el.children)

def codebox_md(div):
    """Конвертирует <div class=codebox> в fenced code block."""
    lines = []
    for p in div.find_all("p", recursive=False):
        cls = " ".join(p.get("class", []))
        # Определяем уровень отступа по классу
        m = re.search(r"codeline(\d*)indent", cls)
        if m:
            level = int(m.group(1)) if m.group(1) else 1
        elif "codeline" in cls:
            level = 0
        else:
            level = 0
        text = p.get_text()
        # Убираем хвостовые пробелы, сохраняем текст
        text = text.rstrip()
        lines.append(INDENT * level + text)
    # Определяем язык: если есть ключевые слова 1C — bsl, иначе text
    joined = "\n".join(lines)
    lang = "bsl" if re.search(r"\b(Функция|Процедура|Возврат|Новый|Если|Пока|Цикл)\b", joined) else "text"
    return f"```{lang}\n{joined}\n```"

def convert_page(html):
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body")
    if not body:
        return ""
    blocks = []
    for el in body.children:
        if isinstance(el, NavigableString):
            t = el.strip()
            if t:
                blocks.append(re.sub(r"\s+", " ", t))
            continue
        name = el.name
        if name in ("script", "style"):
            continue
        cls = " ".join(el.get("class", []))
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            t = inline_children(el).strip()
            if t:
                blocks.append(f"## {t}")
        elif name == "div" and "codebox" in cls:
            blocks.append(codebox_md(el))
        elif name == "p":
            if "listingnazv" in cls:
                t = re.sub(r"\s+", " ", el.get_text()).strip()
                if t:
                    blocks.append(f"**{t}**")
            elif "vrezkanazv" in cls:
                blocks.append("> **Подробнее**")
            elif "vrezkabody" in cls:
                t = inline_children(el).strip()
                if t:
                    blocks.append(f"> {t}")
            elif "picyakor" in cls:
                img = el.find("img")
                if img:
                    src = img.get("src", "")
                    blocks.append(f"![image]({src})")
            elif "picnazv" in cls:
                t = re.sub(r"\s+", " ", el.get_text()).strip()
                if t:
                    blocks.append(f"*{t}*")
            else:
                t = inline_children(el).strip()
                if t:
                    blocks.append(t)
        elif name == "div":
            t = inline_children(el).strip()
            if t:
                blocks.append(t)
        elif name == "ul" or name == "ol":
            items = []
            for li in el.find_all("li", recursive=False):
                items.append(f"- {inline_children(li).strip()}")
            blocks.append("\n".join(items))
    # Очистка: убираем пустые блоки, схлопываем лишние пустые строки
    clean = [b for b in blocks if b.strip()]
    return "\n\n".join(clean) + "\n"

def main():
    # Если передан pid — конвертируем одну страницу (для теста)
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
        src = os.path.join(RAW, f"{pid:03d}.html")
        if not os.path.exists(src):
            # пробуем образец
            src = os.path.join(BASE, "_sample_pid33.html")
            pid = 33
        with open(src, encoding="utf-8") as f:
            html = f.read()
        md = convert_page(html)
        out = os.path.join(MD, f"{pid:03d}.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"pid={pid} -> {out} ({len(md)} chars)")
        print("=" * 60)
        print(md[:2000])
        return

    # Иначе — все страницы
    id2title = {}
    tf = os.path.join(BASE, "_id2title.json")
    if os.path.exists(tf):
        with open(tf, encoding="utf-8") as f:
            id2title = json.load(f)

    converted = 0
    missing = 0
    for fname in sorted(os.listdir(RAW)):
        if not fname.endswith(".html"):
            continue
        pid = fname[:-5]
        with open(os.path.join(RAW, fname), encoding="utf-8") as f:
            html = f.read()
        md = convert_page(html)
        with open(os.path.join(MD, f"{pid}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        converted += 1
    print(f"Конвертировано: {converted} страниц")

if __name__ == "__main__":
    main()
