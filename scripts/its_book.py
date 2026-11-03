# -*- coding: utf-8 -*-
"""
its_book.py — универсальный скачиватель книг с its.1c.ru в Markdown для Obsidian.

Одной командой делает весь пайплайн для ЛЮБОЙ книги (параметр --book):
  1. warm-up сессии (GET главной страницы книги) — иначе контентные страницы дают 401
  2. обнаружение страниц (max pid из дерева оглавления li id="toc_N")
  3. скачивание всех страниц (raw HTML из iframe#w_metadata_doc_frame, srcdoc или src)
  4. маппинг pid → заголовок (из дерева оглавления)
  5. конвертация HTML → Markdown (понимает классы 1C ITS)
  6. обнаружение базового URL картинок (тег <base> в HTML страницы)
  7. скачивание всех картинок в images/ + подмена ссылок в md
  8. сборка TOC.md (группировка по «Глава N»)
  9. переименование NNN.md → NNN. <Заголовок>.md
  10. копирование готовой папки в Obsidian (output)

Использование:
  python its_book.py --book intgr83 --output "C:\\Voult\\Volt\\1c\\Книги1сИтс\\Технологии интеграции"
  python its_book.py --book <id> --output <папка> --title "Название книги"
  python its_book.py --book <id> --output <папка> --skip-download   # raw уже скачан
  python its_book.py --book <id> --output <папка> --skip-images     # без картинок

Куки сессии (общие для всех книг) по умолчанию:
  C:\\AI_PROJECTS\\QWEN_LOC\\scripts\\its_pages\\_session_cookies.json
"""
import argparse
import json
import os
import random
import re
import shutil
import sys
import time

import requests
from bs4 import BeautifulSoup, NavigableString

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.8078.48 Safari/537.36")
DEFAULT_COOKIES = r"C:\AI_PROJECTS\QWEN_LOC\scripts\its_pages\_session_cookies.json"
INDENT = "    "  # 4 пробела на уровень отступа кода
ILLEGAL = r'[<>:"/\\|?*\x00-\x1f]'


# --------------------------------------------------------------------------- #
#  Сессия / сеть
# --------------------------------------------------------------------------- #
def load_session(cookies_path, home_url):
    with open(cookies_path, encoding="utf-8") as f:
        cookies = json.load(f)
    s = requests.Session()
    for c in cookies:
        s.cookies.set(c["name"], c["value"], domain=c.get("domain", "its.1c.ru"),
                      path=c.get("path", "/"))
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Referer": home_url,
    })
    return s


def fetch_home(s, home_url):
    """Warm-up: GET главной страницы. Возвращает HTML главной."""
    r = s.get(home_url, timeout=40)
    if r.status_code == 401:
        raise RuntimeError(
            f"Главная страница {home_url} вернула 401. "
            "Куки сессии недействительны — нужен новый логин в its.1c.ru.")
    time.sleep(random.uniform(1.0, 2.0))
    return r.text


# --------------------------------------------------------------------------- #
#  Обнаружение страниц и заголовков
# --------------------------------------------------------------------------- #
def discover_pages(home_html, book):
    """Из дерева оглавления (li id="toc_N") возвращает (max_pid, id2title)."""
    soup = BeautifulSoup(home_html, "lxml")
    id2title = {}
    for li in soup.find_all("li", id=re.compile(r"^toc_\d+$")):
        tid = int(li["id"].split("_")[1])
        a = li.find("a", href=re.compile(r"/db/" + re.escape(book) + r"/content/\d+/hdoc"))
        if a:
            id2title[tid] = a.get_text(strip=True)
    if not id2title:
        raise RuntimeError(
            "В главной странице не найдено дерева оглавления (li id=\"toc_N\"). "
            "Возможно, структура книги отличается или нет доступа.")
    max_pid = max(id2title.keys())
    return max_pid, id2title


def extract_content(s, book, pid):
    """Возвращает (html, status). status: ok|restricted|error"""
    url = f"https://its.1c.ru/db/{book}/content/{pid}/hdoc"
    r = s.get(url, timeout=40)
    if r.status_code == 401:
        return None, "restricted"
    soup = BeautifulSoup(r.text, "lxml")
    iframe = soup.find("iframe", id="w_metadata_doc_frame")
    if not iframe:
        return None, "error"
    if iframe.get("srcdoc"):
        return iframe["srcdoc"], "ok"
    src = iframe.get("src")
    if src:
        rs = s.get("https://its.1c.ru" + src, timeout=40)
        if rs.status_code == 401:
            return None, "restricted"
        return rs.text, "ok"
    return None, "error"


def download_pages(s, book, max_pid, raw_dir, home_url):
    """Скачивает страницы 1..max_pid в raw_dir/NNN.html. Resume по размеру файла."""
    os.makedirs(raw_dir, exist_ok=True)
    ok = restricted = error = skipped = 0
    for pid in range(1, max_pid + 1):
        fname = os.path.join(raw_dir, f"{pid:03d}.html")
        if os.path.exists(fname) and os.path.getsize(fname) > 500:
            skipped += 1
            continue
        html = None
        status = "error"
        for attempt in range(1, 4):
            try:
                html, status = extract_content(s, book, pid)
            except Exception as e:
                status, html = "error", None
                print(f"  pid={pid} attempt {attempt} exception: {e}", flush=True)
            if status == "ok":
                break
            time.sleep(random.uniform(2.0, 4.0) * attempt)
        if status == "ok" and html:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(html)
            ok += 1
            if pid % 25 == 0 or pid == max_pid:
                print(f"  [{pid}/{max_pid}] ok={ok} restricted={restricted} "
                      f"error={error} skipped={skipped}", flush=True)
        else:
            if status == "restricted":
                restricted += 1
            else:
                error += 1
        time.sleep(random.uniform(0.8, 1.6))
    print(f"Страницы: ok={ok} restricted={restricted} error={error} skipped={skipped} "
          f"(всего {max_pid})")
    return ok, restricted, error, skipped


# --------------------------------------------------------------------------- #
#  Конвертация HTML → Markdown (логика из its_convert.py)
# --------------------------------------------------------------------------- #
def inline_md(node):
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
    lines = []
    for p in div.find_all("p", recursive=False):
        cls = " ".join(p.get("class", []))
        m = re.search(r"codeline(\d*)indent", cls)
        if m:
            level = int(m.group(1)) if m.group(1) else 1
        else:
            level = 0
        text = p.get_text().rstrip()
        lines.append(INDENT * level + text)
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
        elif name in ("ul", "ol"):
            items = [f"- {inline_children(li).strip()}"
                     for li in el.find_all("li", recursive=False)]
            blocks.append("\n".join(items))
    clean = [b for b in blocks if b.strip()]
    return "\n\n".join(clean) + "\n"


def convert_all(raw_dir, md_dir):
    os.makedirs(md_dir, exist_ok=True)
    converted = 0
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith(".html"):
            continue
        pid = fname[:-5]
        with open(os.path.join(raw_dir, fname), encoding="utf-8") as f:
            html = f.read()
        md = convert_page(html)
        with open(os.path.join(md_dir, f"{pid}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        converted += 1
    print(f"Конвертировано: {converted} страниц")
    return converted


# --------------------------------------------------------------------------- #
#  Картинки
# --------------------------------------------------------------------------- #
def discover_image_base(raw_dir):
    """Читает тег <base> в raw HTML и возвращает базовый URL каталога картинок."""
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith(".html"):
            continue
        html = open(os.path.join(raw_dir, fname), encoding="utf-8").read()
        soup = BeautifulSoup(html, "lxml")
        base = soup.find("base")
        if base and base.get("href"):
            href = base["href"]  # вида /db/content/intgr83/src/13.html
            m = re.match(r"(/db/content/[^/]+/src/)", href)
            if m:
                return "https://its.1c.ru" + m.group(1)
    # Фолбэк: стандартный паттерн (нужен book — передаём через глобальную переменную)
    return None


def collect_images(raw_dir):
    """Собирает уникальные ОТСОСИТЕЛЬНЫЕ картинки: file_name -> token."""
    images = {}
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith(".html"):
            continue
        html = open(os.path.join(raw_dir, fname), encoding="utf-8").read()
        soup = BeautifulSoup(html, "lxml")
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            if src.startswith("http://") or src.startswith("https://") or src.startswith("//"):
                continue
            if "?" in src:
                file_name, query = src.split("?", 1)
                m = re.search(r"_=([^&]+)", query)
                token = m.group(1) if m else None
            else:
                file_name, token = src, None
            file_name = file_name.strip()
            if file_name and file_name not in images:
                images[file_name] = token
    return images


def download_images(s, images, img_base, images_dir, home_url):
    os.makedirs(images_dir, exist_ok=True)
    downloaded, failed = {}, []
    for i, (file_name, token) in enumerate(images.items(), 1):
        local_path = os.path.join(images_dir, file_name)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 100:
            downloaded[file_name] = local_path
            continue
        url = img_base + file_name
        if token:
            url += "?_=" + token
        ok = False
        for attempt in range(3):
            try:
                r = s.get(url, timeout=40)
                if r.status_code == 200 and len(r.content) > 100:
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    downloaded[file_name] = local_path
                    ok = True
                    break
                elif token:
                    url = img_base + file_name  # пробуем без токена
            except Exception as e:
                if attempt == 2:
                    failed.append({"file": file_name, "url": url, "error": str(e)})
        if not ok and not any(f["file"] == file_name for f in failed):
            failed.append({"file": file_name, "url": url})
        if i % 20 == 0 or i == len(images):
            print(f"  [{i}/{len(images)}] скачано={len(downloaded)} ошибок={len(failed)}",
                  flush=True)
        time.sleep(random.uniform(0.2, 0.5))
    print(f"Картинки: скачано={len(downloaded)} ошибок={len(failed)}")
    if failed:
        for f in failed[:20]:
            print(f"  НЕ СКАЧАЛАСЬ: {f['file']}  {f.get('url', '')}")
    return downloaded, failed


def update_md_links(md_dir, images):
    """Подменяет ![image](<файл>?_=...) → ![image](images/<файл>) во всех md."""
    updated = 0
    for fname in os.listdir(md_dir):
        if not fname.endswith(".md") or fname == "TOC.md":
            continue
        fpath = os.path.join(md_dir, fname)
        content = open(fpath, encoding="utf-8").read()
        new_content = content
        for file_name in images:
            pattern = re.compile(r'!\[[^\]]*\]\(' + re.escape(file_name) + r'(?:\?[^)]*)?\)')
            if pattern.search(new_content):
                new_content = pattern.sub(f'![image](images/{file_name})', new_content)
        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1
    print(f"Обновлено MD-ссылок на картинки: {updated} файлов")
    return updated


# --------------------------------------------------------------------------- #
#  TOC + переименование
# --------------------------------------------------------------------------- #
def sanitize(title):
    t = re.sub(ILLEGAL, " ", title)
    t = re.sub(r"\s+", " ", t).strip().rstrip(".")
    return t


def fname(pid, title):
    return f"{pid:03d}. {sanitize(title)}.md"


def rename_files(md_dir, id2title):
    renamed = skipped = 0
    for pid_str, title in id2title.items():
        if pid_str == "999999":
            continue
        pid = int(pid_str)
        src = os.path.join(md_dir, f"{pid:03d}.md")
        dst = os.path.join(md_dir, fname(pid, title))
        if not os.path.exists(src):
            skipped += 1
            continue
        if src == dst or os.path.exists(dst):
            skipped += 1
            continue
        os.rename(src, dst)
        renamed += 1
    print(f"Переименовано: {renamed}, пропущено: {skipped}")
    return renamed


def build_toc(md_dir, id2title, book_title, total_pages):
    pages = [(int(p), t) for p, t in id2title.items() if p != "999999"]
    pages.sort(key=lambda x: x[0])
    chapters, front, current = [], [], None
    for pid, title in pages:
        if re.match(r"^Глава\s+\d", title):
            current = (title, [])
            chapters.append(current)
        elif current is None:
            front.append((pid, title))
        else:
            current[1].append((pid, title))

    def md_link(pid, title):
        fn = fname(pid, title)
        if os.path.exists(os.path.join(md_dir, fn)):
            return f"[{title}]({fn})"
        return f"{title} *(нет файла)*"

    lines = [f"# {book_title}", "",
             f"Полный текст книги ({total_pages} страниц), скачанный с its.1c.ru "
             "и сконвертированный в Markdown.", "",
             f"Всего страниц: {len(pages)}", ""]
    if front:
        lines += ["## Предварительные страницы", ""]
        lines += [f"- {md_link(pid, title)}" for pid, title in front]
        lines.append("")
    for chap_title, chap_pages in chapters:
        lines += [f"## {chap_title}", ""]
        lines += [f"- {md_link(pid, title)}" for pid, title in chap_pages]
        lines.append("")
    lines += ["---", "", "## Структура файлов", "",
              "- `NNN. Название.md` — текст страницы (NNN — номер, Название — заголовок)",
              "- `TOC.md` — это оглавление со ссылками на все страницы",
              "- `images/` — картинки из книги", ""]
    toc_path = os.path.join(md_dir, "TOC.md")
    with open(toc_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"TOC.md собран: {len(front)} фронт-стр., {len(chapters)} глав, "
          f"{len(pages)} страниц")
    return toc_path


# --------------------------------------------------------------------------- #
#  Копирование в Obsidian
# --------------------------------------------------------------------------- #
def copy_to_output(md_dir, images_dir, output):
    os.makedirs(output, exist_ok=True)
    copied_md = 0
    for fname in os.listdir(md_dir):
        if fname.endswith(".md"):
            shutil.copy2(os.path.join(md_dir, fname), os.path.join(output, fname))
            copied_md += 1
    if os.path.isdir(images_dir) and os.listdir(images_dir):
        dst_img = os.path.join(output, "images")
        if os.path.isdir(dst_img):
            shutil.rmtree(dst_img)
        shutil.copytree(images_dir, dst_img)
    print(f"Скопировано в Obsidian: {copied_md} md-файлов + images/ → {output}")
    return copied_md


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Скачивание книги с its.1c.ru в Markdown")
    ap.add_argument("--book", required=True, help="ID книги, напр. intgr83")
    ap.add_argument("--output", required=True, help="Папка Obsidian для готовых md")
    ap.add_argument("--cookies", default=DEFAULT_COOKIES, help="Путь к _session_cookies.json")
    ap.add_argument("--workdir", default=None,
                    help="Рабочая папка (по умолчанию scripts/its_pages_<book>)")
    ap.add_argument("--title", default=None, help="Название книги для TOC (по умолчанию = book)")
    ap.add_argument("--skip-download", action="store_true", help="Не скачивать страницы (raw уже есть)")
    ap.add_argument("--skip-images", action="store_true", help="Не скачивать картинки")
    args = ap.parse_args()

    book = args.book
    home_url = f"https://its.1c.ru/db/{book}"
    book_title = args.title or book
    workdir = args.workdir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), f"its_pages_{book}")
    raw_dir = os.path.join(workdir, "raw")
    md_dir = os.path.join(workdir, "md")
    images_dir = os.path.join(workdir, "images")
    os.makedirs(workdir, exist_ok=True)

    print(f"=== Книга: {book} ===")
    print(f"    Home:    {home_url}")
    print(f"    Workdir: {workdir}")
    print(f"    Output:  {args.output}")
    print()

    s = load_session(args.cookies, home_url)

    # 1. Warm-up + главная
    print("[1/9] Warm-up + главная страница...")
    home_html = fetch_home(s, home_url)
    with open(os.path.join(workdir, "_home.html"), "w", encoding="utf-8") as f:
        f.write(home_html)

    # 2. Обнаружение страниц
    print("[2/9] Обнаружение страниц...")
    max_pid, id2title = discover_pages(home_html, book)
    print(f"    Найдено страниц в оглавлении: {len(id2title)}, max_pid={max_pid}")
    with open(os.path.join(workdir, "_id2title.json"), "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in id2title.items()}, f, ensure_ascii=False, indent=2)

    # 3. Скачивание страниц
    if args.skip_download:
        print("[3/9] Скачивание страниц — ПРОПУЩЕНО (--skip-download)")
    else:
        print("[3/9] Скачивание страниц...")
        download_pages(s, book, max_pid, raw_dir, home_url)

    # 4. Конвертация
    print("[4/9] Конвертация HTML → Markdown...")
    convert_all(raw_dir, md_dir)

    # 5-7. Картинки
    if args.skip_images:
        print("[5/9] Картинки — ПРОПУЩЕНЫ (--skip-images)")
    else:
        print("[5/9] Обнаружение базового URL картинок...")
        img_base = discover_image_base(raw_dir)
        if not img_base:
            img_base = f"https://its.1c.ru/db/content/{book}/src/"
            print(f"    <base> не найден, использую фолбэк: {img_base}")
        else:
            print(f"    Базовый URL картинок: {img_base}")
        print("[6/9] Сборка списка картинок...")
        images = collect_images(raw_dir)
        print(f"    Уникальных картинок: {len(images)}")
        print("[7/9] Скачивание картинок...")
        if images:
            download_images(s, images, img_base, images_dir, home_url)
            update_md_links(md_dir, images)

    # 8. TOC
    print("[8/9] Сборка TOC.md...")
    build_toc(md_dir, id2title, book_title, max_pid)

    # 9. Переименование + копирование
    print("[9/9] Переименование + копирование в Obsidian...")
    rename_files(md_dir, id2title)
    copy_to_output(md_dir, images_dir, args.output)

    print()
    print("=== ГОТОВО ===")
    print(f"Готовая папка: {args.output}")
    print(f"  - md-файлы: NNN. <Заголовок>.md")
    print(f"  - TOC.md — оглавление со ссылками")
    print(f"  - images/ — картинки")


if __name__ == "__main__":
    main()
