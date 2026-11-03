# -*- coding: utf-8 -*-
"""
Конвертирует диалоги "Режим ИИ" (Google Takeout, МоиДействия.html) в
отдельные Markdown-файлы, по одному на диалог. Формат — как у ChatGPT:
заголовок, метаданные (Создан, Модель), затем блоки 👤 Пользователь / 🤖 Gemini.

Вложения (картинки) копируются в папку attachments/ и линкуются через
Obsidian-синтаксис ![[...]].

Использование:
    py gemini_to_md.py [файл МоиДействия.html] [папка вывода Obsidian]

Без аргументов:
    src  = D:\тексты для тракт\DeepSeek\googl\2-10-26\extracted\Takeout\Мои действия\Режим ИИ\МоиДействия.html
    out  = C:\Voult\Volt\Gemini
"""
import os
import re
import shutil
import sys
from bs4 import BeautifulSoup, NavigableString, Tag

DEFAULT_SRC = r"D:\тексты для тракт\DeepSeek\googl\2-10-26\extracted\Takeout\Мои действия\Режим ИИ\МоиДействия.html"
DEFAULT_OUT = r"C:\Voult\Volt\Gemini"

MONTHS = {
    'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6,
    'июл': 7, 'авг': 8, 'сент': 9, 'окт': 10, 'нояб': 11, 'дек': 12,
}


def resolve_paths():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    return src, out


def sanitize_filename(name, max_len=80):
    name = re.sub(r"[\r\n\t\f\v]", " ", name)
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name.strip())
    if len(name) > max_len:
        name = name[:max_len].rstrip("_")
    return name or "без_названия"


def parse_timestamp(ts):
    """'26 окт. 2026 г., 21:51:09 MSK' → '2026-10-26 21:51:09' (полный, для сортировки).

    Если распознать не удалось — возвращает "" (пустую строку), чтобы
    строка «Создан:» не вставлялась в вывод.
    """
    if not ts:
        return ""
    ts = ts.strip()
    m = re.match(r"(\d{1,2})\s+([а-яё]+)\.?\s+(\d{4})\s*г?\.?,?\s*(\d{1,2}:\d{2}(?::\d{2})?)", ts)
    if m:
        day = int(m.group(1))
        month_abbr = m.group(2).lower()
        year = int(m.group(3))
        time_str = m.group(4)
        month = None
        for abbr, num in MONTHS.items():
            if month_abbr.startswith(abbr):
                month = num
                break
        if month:
            return f"{year:04d}-{month:02d}-{day:02d} {time_str}"
    return ""


def strip_user_intent(text):
    """Убирает комментарии <!-- User Intent: ... --> из текста."""
    return re.sub(r"<!--\s*User Intent:.*?-->", "", text, flags=re.DOTALL)


def element_to_md(el, attach_dir, src_dir):
    """Рекурсивно конвертирует BeautifulSoup-элемент в Markdown."""
    if isinstance(el, NavigableString):
        text = str(el)
        text = strip_user_intent(text)
        return text

    if not isinstance(el, Tag):
        return str(el)

    name = el.name

    if name in ("strong", "b"):
        inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
        inner = inner.strip()
        if inner:
            return f"**{inner}**"
        return ""

    if name in ("em", "i"):
        inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
        inner = inner.strip()
        if inner:
            return f"*{inner}*"
        return ""

    if name == "a":
        inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
        inner = inner.strip()
        href = el.get("href", "")
        if href and inner:
            return f"[{inner}]({href})"
        return inner

    if name == "img":
        src = el.get("src", "")
        if src and os.path.isfile(os.path.join(src_dir, src)):
            safe_name = sanitize_filename(src, max_len=100)
            dest = os.path.join(attach_dir, safe_name)
            if not os.path.exists(dest):
                os.makedirs(attach_dir, exist_ok=True)
                shutil.copy2(os.path.join(src_dir, src), dest)
            return f"![[{safe_name}]]"
        return f"*📎 Изображение: {src}*"

    if name == "br":
        return "\n"

    if name == "p":
        inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
        inner = inner.strip()
        if inner:
            return inner + "\n\n"
        return ""

    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(name[1])
        inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
        inner = inner.strip()
        if inner:
            return f"{'#' * level} {inner}\n\n"
        return ""

    if name in ("ul", "ol"):
        items = []
        for i, li in enumerate(el.find_all("li", recursive=False), 1):
            inner = "".join(element_to_md(c, attach_dir, src_dir) for c in li.children)
            inner = inner.strip()
            if el.name == "ol":
                items.append(f"{i}. {inner}")
            else:
                items.append(f"- {inner}")
        if items:
            return "\n".join(items) + "\n\n"
        return ""

    if name == "div":
        inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
        inner = inner.strip()
        if inner:
            return inner + "\n\n"
        return ""

    # Default: extract text
    inner = "".join(element_to_md(c, attach_dir, src_dir) for c in el.children)
    return inner


def extract_after_marker(p, marker_text):
    """
    Из <p> с маркером (<strong>marker_text</strong><br>CONTENT) извлекает
    CONTENT — всё, что после <strong> с маркером.
    Возвращает список BeautifulSoup-элементов (или строк).
    """
    for s in p.find_all("strong"):
        if marker_text in s.get_text():
            parts = []
            for sib in s.next_siblings:
                if isinstance(sib, Tag) and sib.name == "br":
                    continue
                parts.append(sib)
            return parts
    return []


def parse_content_cell(cell, attach_dir, src_dir):
    """
    Разбирает основной content-cell на сегменты (role, content).
    role: 'user' | 'assistant'
    content: список BeautifulSoup-элементов (или строк)
    """
    segments = []
    current_role = None
    current_content = []

    def flush():
        nonlocal current_role, current_content
        if current_role is not None and current_content:
            segments.append((current_role, current_content))
        current_content = []

    for child in cell.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text and current_role is not None:
                current_content.append(child)
            continue

        if not isinstance(child, Tag):
            continue

        if child.name == "p":
            p_text = child.get_text()
            if "Ваш запрос:" in p_text:
                flush()
                current_role = "user"
                parts = extract_after_marker(child, "Ваш запрос:")
                current_content.extend(parts)
            elif "Ответ Поиска:" in p_text:
                flush()
                current_role = "assistant"
                parts = extract_after_marker(child, "Ответ Поиска:")
                current_content.extend(parts)
            else:
                # Продолжение текущего ответа
                if current_role is not None:
                    current_content.append(child)
        else:
            # Другие элементы (h3, ul, ol, div, etc.)
            if current_role is not None:
                current_content.append(child)

    flush()
    return segments


def extract_timestamp(cell):
    """Извлекает timestamp из content-cell.

    Точка после месяца опциональна: «мая» пишется без точки
    (янв., фев., мар., апр., мая, июн., ...), поэтому `\.?`.
    """
    for child in cell.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if re.match(r"\d{1,2}\s+[а-яё]+\.?\s+\d{4}\s*г", text):
                return text
    return ""


def extract_title(cell):
    """Извлекает заголовок (текст ссылки после 'Выполнен поиск')."""
    for child in cell.children:
        if isinstance(child, Tag) and child.name == "a":
            text = child.get_text(strip=True)
            if text:
                return text
    # Fallback: первый текст
    text = cell.get_text(strip=True)
    if text:
        return text[:80]
    return "Без названия"


BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "div", "table", "blockquote", "pre"}


def content_to_md(content, attach_dir, src_dir):
    """Склеивает элементы content в Markdown.

    Блочные элементы (<p>, <h3>, <ul>, ...) отделяются от предшествующего
    инлайн-текста пустой строкой — иначе текст «прилипает»:
    «...Тихом океане.Японское командование...».
    """
    md = ""
    for c in content:
        if isinstance(c, Tag):
            part = element_to_md(c, attach_dir, src_dir)
            if c.name in BLOCK_TAGS and md and not md.endswith("\n"):
                md += "\n\n"
            md += part
        else:
            md += str(c)
    md = strip_user_intent(md)
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def entry_to_md(cell, attach_dir, src_dir):
    """Конвертирует один outer-cell в Markdown."""
    # Находим основной content-cell (не text-right)
    main_cell = None
    for cc in cell.select("div.content-cell.mdl-cell--6-col.mdl-typography--body-1"):
        classes = cc.get("class") or []
        if "mdl-typography--text-right" not in classes:
            main_cell = cc
            break

    if main_cell is None:
        return None

    timestamp = extract_timestamp(main_cell)
    title = extract_title(main_cell)
    ts_full = parse_timestamp(timestamp)
    # Только дата (без времени) — по требованию пользователя
    ts_date = ts_full.split(" ")[0] if ts_full else ""

    segments = parse_content_cell(main_cell, attach_dir, src_dir)

    if not segments:
        return None

    lines = []
    lines.append(f"# {title}")
    lines.append("")

    # Блок метаданных — как у ChatGPT/DeepSeek, но только строки,
    # для которых есть данные (у Gemini нет ID и времени обновления).
    # «Создан:» вставляется только если дата распознана.
    meta = []
    if ts_date:
        meta.append(f"> Создан: {ts_date}")
    meta.append("> Модель: Режим ИИ (Gemini)")
    for j in range(len(meta)):
        # Две пробела в конце — Markdown-перенос строки (кроме последней)
        lines.append(meta[j] + ("  " if j < len(meta) - 1 else ""))

    lines.append("")
    lines.append("---")
    lines.append("")

    for role, content in segments:
        if role == "user":
            lines.append("## 👤 Пользователь")
            lines.append("")
            text = content_to_md(content, attach_dir, src_dir)
            if text:
                lines.append(text)
                lines.append("")
        elif role == "assistant":
            lines.append("## 🤖 Gemini")
            lines.append("")
            md = content_to_md(content, attach_dir, src_dir)
            if md:
                lines.append(md)
                lines.append("")

    return "\n".join(lines)


def main():
    src_file, out_dir = resolve_paths()

    if not os.path.isfile(src_file):
        print(f"Ошибка: файл не найден: {src_file}")
        sys.exit(1)

    src_dir = os.path.dirname(src_file)
    attach_dir = os.path.join(out_dir, "attachments")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Читаю: {src_file}")
    with open(src_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    cells = soup.select("div.outer-cell")
    print(f"Всего записей: {len(cells)}")

    # Собираем только записи с диалогами (есть "Ваш запрос")
    dialog_cells = []
    for cell in cells:
        text = cell.get_text(" ", strip=True)
        if "Ваш запрос" in text:
            dialog_cells.append(cell)

    print(f"Записей с диалогами: {len(dialog_cells)}")

    # Сортируем по timestamp: новые в начало, старые в конец
    def get_ts(cell):
        for cc in cell.select("div.content-cell.mdl-cell--6-col.mdl-typography--body-1"):
            classes = cc.get("class") or []
            if "mdl-typography--text-right" not in classes:
                ts = extract_timestamp(cc)
                return parse_timestamp(ts)
        return ""

    dialog_cells.sort(key=get_ts, reverse=True)

    written = 0
    for i, cell in enumerate(dialog_cells, 1):
        md = entry_to_md(cell, attach_dir, src_dir)
        if md is None:
            continue
        title = extract_title(
            next(
                (
                    cc
                    for cc in cell.select("div.content-cell.mdl-cell--6-col.mdl-typography--body-1")
                    if "mdl-typography--text-right" not in (cc.get("class") or [])
                ),
                cell,
            )
        )
        fname = f"{i:03d}_{sanitize_filename(title)}.md"
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        written += 1

    print(f"\nГотово: {written} файлов в {out_dir}")
    if os.path.isdir(attach_dir):
        n_att = len(os.listdir(attach_dir))
        print(f"Вложений скопировано: {n_att} → {attach_dir}")


if __name__ == "__main__":
    main()
