# -*- coding: utf-8 -*-
"""
Разбивает выгрузку DeepSeek (conversations.json) на отдельные Markdown-файлы,
по одному на диалог. Сохраняет чистый текст «пользователь -> ответ».
THINK / SEARCH / TOOL_* отбрасываются. Прикреплённые файлы помечаются строкой.

Использование:
    py deepseek_to_md.py [путь к conversations.json или папке] [папка вывода]

Без аргументов — берёт последнюю известную выгрузку, вывод в ту же папку,
что и исходный файл.
"""
import json
import os
import re
import sys

DEFAULT_SRC = r"D:\тексты для тракт\DeepSeek\deepseek_data-2026-10-21\conversations.json"


def resolve_paths():
    if len(sys.argv) > 1:
        p = sys.argv[1]
        src = os.path.join(p, "conversations.json") if os.path.isdir(p) else p
    else:
        src = DEFAULT_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(src)
    return src, out


def fmt_date(iso_str):
    """ISO '2025-07-23T13:31:28.081000+08:00' → '2025-07-23 13:31'."""
    if not iso_str:
        return ""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str


def fmt_msg_date(iso_str):
    """ISO '2025-07-23T13:31:28.081000+08:00' → '2025-07-23' (только дата)."""
    if not iso_str:
        return ""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""


def sanitize_filename(name, max_len=80):
    # Убираем управляющие символы (переносы, табы) и невалидные для имени файла
    name = re.sub(r"[\r\n\t\f\v]", " ", name)
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name.strip())
    if len(name) > max_len:
        name = name[:max_len].rstrip("_")
    return name or "без_названия"


def collect_messages(mapping):
    """Обход дерева от root (DFS), возвращает список message-объектов в порядке диалога."""
    result = []

    def dfs(node_id):
        node = mapping.get(node_id)
        if not node:
            return
        if node.get("message"):
            result.append(node["message"])
        for child in node.get("children", []):
            dfs(child)

    dfs("root")
    return result


def get_model(conv):
    """Берёт model из первого сообщения с ней."""
    mapping = conv.get("mapping", {})
    def dfs(node_id):
        node = mapping.get(node_id)
        if not node:
            return None
        msg = node.get("message")
        if msg and msg.get("model"):
            return msg["model"]
        for child in node.get("children", []):
            r = dfs(child)
            if r:
                return r
        return None
    return dfs("root") or ""


def conversation_to_md(conv):
    lines = []
    title = conv.get("title", "Без названия")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> ID: `{conv.get('id', '')}`  ")
    lines.append(f"> Создан: {fmt_date(conv.get('inserted_at', ''))}  ")
    lines.append(f"> Обновлён: {fmt_date(conv.get('updated_at', ''))}  ")
    model = get_model(conv)
    if model:
        lines.append(f"> Модель: {model}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for msg in collect_messages(conv.get("mapping", {})):
        # Дата сообщения (только дата) — в заголовке блока
        mdate = fmt_msg_date(msg.get("inserted_at", ""))
        suffix = f" · {mdate}" if mdate else ""
        for frag in msg.get("fragments", []):
            ftype = frag.get("type")
            if ftype == "REQUEST":
                content = frag.get("content", "")
                if not content:
                    continue
                lines.append(f"## 👤 Пользователь{suffix}")
                lines.append("")
                lines.append(content)
                lines.append("")
            elif ftype == "RESPONSE":
                content = frag.get("content", "")
                if not content:
                    continue
                lines.append(f"## 🤖 DeepSeek{suffix}")
                lines.append("")
                lines.append(content)
                lines.append("")
            elif ftype == "FILE":
                files = frag.get("files", [])
                names = ", ".join(f.get("file_name", "?") for f in files)
                lines.append(f"*📎 Прикреплённый файл: {names}*")
                lines.append("")
            # THINK / SEARCH / TOOL_* — намеренно пропускаем

    return "\n".join(lines)


def main():
    src, out_dir = resolve_paths()
    if not os.path.isfile(src):
        print(f"Ошибка: файл не найден: {src}")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)

    with open(src, encoding="utf-8") as f:
        data = json.load(f)

    # Сортируем по дате создания: новые в начало, старые в конец
    data.sort(key=lambda c: c.get("inserted_at", ""), reverse=True)

    written = 0
    for i, conv in enumerate(data, 1):
        title = conv.get("title", "Без названия")
        fname = f"{i:03d}_{sanitize_filename(title)}.md"
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(conversation_to_md(conv))
        written += 1

    print(f"Готово: создано {written} файлов в {out_dir}")


if __name__ == "__main__":
    main()
