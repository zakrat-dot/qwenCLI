# -*- coding: utf-8 -*-
"""
Разбивает выгрузку ChatGPT (conversations-*.json) на отдельные Markdown-файлы,
по одному на диалог. Вложения: текст — инлайн, картинки/файлы — копируются
в папку attachments/ и линкуются через Obsidian-синтаксис ![[...]] / [[...]].

Использование:
    py chatgpt_to_md.py [папка экспорта ChatGPT] [папка вывода Obsidian]

Без аргументов:
    src  = D:\тексты для тракт\DeepSeek\ChatGPT
    out  = C:\Voult\Volt\ChatGPT
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

DEFAULT_SRC = r"D:\тексты для тракт\DeepSeek\ChatGPT"
DEFAULT_OUT = r"C:\Voult\Volt\ChatGPT"


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


def fmt_ts(ts):
    """Unix timestamp → 'YYYY-MM-DD HH:MM'."""
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def fmt_msg_date(ts):
    """Unix timestamp → 'YYYY-MM-DD' (только дата, UTC — как в шапке)."""
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


def collect_messages(mapping, current_node):
    """Обход от current_node к root по parent-ссылкам, затем разворот."""
    chain = []
    node_id = current_node
    seen = set()
    while node_id and node_id not in seen:
        seen.add(node_id)
        node = mapping.get(node_id)
        if not node:
            break
        if node.get("message"):
            chain.append(node["message"])
        node_id = node.get("parent")
    chain.reverse()
    return chain


def load_asset_names(src_dir):
    """Загружает карту .dat → оригинальное имя."""
    path = os.path.join(src_dir, "conversation_asset_file_names.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def handle_attachment(att, src_dir, asset_names, attach_dir):
    """
    Обрабатывает вложение. Возвращает строку для вставки в MD.
    Текст — инлайн, бинарные — копирует в attach_dir и линкует.
    """
    att_id = att.get("id", "")
    dat_name = att_id + ".dat"
    dat_path = os.path.join(src_dir, dat_name)
    orig_name = asset_names.get(dat_name, att.get("name", att_id))
    mime = att.get("mime_type", "")

    if not os.path.isfile(dat_path):
        return f"*📎 Вложение (файл не найден): {orig_name}*"

    # Текст — вставляем содержимое
    if mime.startswith("text/") or orig_name.lower().endswith((".md", ".txt", ".csv", ".json", ".xml", ".html")):
        try:
            with open(dat_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
            if len(content) > 50_000:
                content = content[:50_000] + "\n\n… *(обрезано, полный файл в attachments/)*"
            return f"*📎 Вложение: {orig_name}*\n\n```\n{content}\n```"
        except Exception:
            pass  # fallback к копированию

    # Бинарные (картинки, PDF, DOCX и т.д.) — копируем в vault
    os.makedirs(attach_dir, exist_ok=True)
    safe_name = sanitize_filename(orig_name, max_len=100)
    dest = os.path.join(attach_dir, safe_name)
    # Если файл с таким именем уже есть — не перетираем
    if not os.path.exists(dest):
        shutil.copy2(dat_path, dest)

    if mime.startswith("image/"):
        return f"*📎 Вложение: {orig_name}*\n\n![[{safe_name}]]"
    return f"*📎 Вложение: {orig_name}*\n\n[[{safe_name}]]"


def extract_parts(parts, src_dir, asset_names, attach_dir):
    """
    Разбирает parts: строки → текст, dict с asset_pointer → картинка.
    Возвращает (text_lines, inline_attachments).
    """
    text_lines = []
    inline_atts = []
    for p in parts:
        if isinstance(p, str):
            if p.strip():
                text_lines.append(p)
        elif isinstance(p, dict):
            ct = p.get("content_type", "")
            if ct == "image_asset_pointer":
                # asset_pointer: "file-service://file-87QHQfSZK8n9nuvE2om5Hh"
                ap = p.get("asset_pointer", "")
                file_id = ap.replace("file-service://", "")
                inline_atts.append({
                    "id": file_id,
                    "name": file_id,
                    "mime_type": "image/*",
                })
            # reasoning_recap, thoughts — пропускаем
    return text_lines, inline_atts


def conversation_to_md(conv, src_dir, asset_names, attach_dir):
    lines = []
    title = conv.get("title", "Без названия")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> ID: `{conv.get('id', '')}`  ")
    lines.append(f"> Создан: {fmt_ts(conv.get('create_time'))}  ")
    lines.append(f"> Обновлён: {fmt_ts(conv.get('update_time'))}  ")
    lines.append(f"> Модель: {conv.get('default_model_slug', '?')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    mapping = conv.get("mapping", {})
    current_node = conv.get("current_node")
    messages = collect_messages(mapping, current_node)

    for msg in messages:
        role = (msg.get("author") or {}).get("role", "")
        content = msg.get("content") or {}
        parts = content.get("parts", [])
        attachments = (msg.get("metadata") or {}).get("attachments", [])

        text_lines, inline_atts = extract_parts(parts, src_dir, asset_names, attach_dir)

        # Дата сообщения (только дата) — в заголовке блока
        mdate = fmt_msg_date(msg.get("create_time"))
        suffix = f" · {mdate}" if mdate else ""

        if role == "user":
            lines.append(f"## 👤 Пользователь{suffix}")
            lines.append("")
            if text_lines:
                lines.append("\n".join(text_lines))
                lines.append("")
            for att in inline_atts + attachments:
                lines.append(handle_attachment(att, src_dir, asset_names, attach_dir))
                lines.append("")
        elif role == "assistant":
            lines.append(f"## 🤖 ChatGPT{suffix}")
            lines.append("")
            if text_lines:
                lines.append("\n".join(text_lines))
                lines.append("")
            for att in inline_atts + attachments:
                lines.append(handle_attachment(att, src_dir, asset_names, attach_dir))
                lines.append("")
        # system / developer — пропускаем

    return "\n".join(lines)


def main():
    src_dir, out_dir = resolve_paths()

    # Собираем все conversations-*.json
    conv_files = sorted(
        f for f in os.listdir(src_dir)
        if f.startswith("conversations-") and f.endswith(".json")
    )
    if not conv_files:
        print(f"Ошибка: не найдено conversations-*.json в {src_dir}")
        sys.exit(1)

    all_convs = []
    for cf in conv_files:
        path = os.path.join(src_dir, cf)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        all_convs.extend(data)
        print(f"  {cf}: {len(data)} диалогов")

    # Сортируем по дате создания: новые в начало, старые в конец
    all_convs.sort(key=lambda c: c.get("create_time", 0), reverse=True)

    asset_names = load_asset_names(src_dir)
    attach_dir = os.path.join(out_dir, "attachments")
    os.makedirs(out_dir, exist_ok=True)

    written = 0
    for i, conv in enumerate(all_convs, 1):
        title = conv.get("title", "Без названия")
        fname = f"{i:03d}_{sanitize_filename(title)}.md"
        path = os.path.join(out_dir, fname)
        md = conversation_to_md(conv, src_dir, asset_names, attach_dir)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        written += 1

    print(f"\nГотово: {written} файлов в {out_dir}")
    if os.path.isdir(attach_dir):
        n_att = len(os.listdir(attach_dir))
        print(f"Вложений скопировано: {n_att} → {attach_dir}")


if __name__ == "__main__":
    main()
