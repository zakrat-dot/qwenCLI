#!/usr/bin/env python3
"""Парсер формата DOXCEL (1С:Предприятие) для анализа структуры."""
import sys
import re

def read_doxcel(path):
    """Читает DOXCEL файл, возвращает (header_info, payload_text).

    Header: MOXCEL (6) + 3x uint16 (6) + [0..N extra 00 bytes] + UTF-8 BOM (3).
    Размер хедера варьируется между файлами, поэтому BOM ищем динамически.
    """
    with open(path, 'rb') as f:
        data = f.read()
    magic = data[:6]
    assert magic == b'MOXCEL', f"Bad magic: {magic}"
    h1 = int.from_bytes(data[6:8], 'little')
    h2 = int.from_bytes(data[8:10], 'little')
    h3 = int.from_bytes(data[10:12], 'little')
    bom_idx = data.find(b'\xef\xbb\xbf')
    assert bom_idx >= 0, "UTF-8 BOM not found in header"
    header_len = bom_idx
    payload = data[bom_idx + 3:].decode('utf-8')
    return (h1, h2, h3, header_len), payload

def parse_value(s, pos):
    """Парсит одно значение из строки, начиная с pos. Возвращает (value, new_pos)."""
    # Пропустить пробелы и запятые
    while pos < len(s) and s[pos] in ' \t\r\n,':
        pos += 1
    if pos >= len(s):
        return None, pos
    c = s[pos]
    if c == '{':
        # Массив/объект
        items = []
        pos += 1
        while pos < len(s):
            while pos < len(s) and s[pos] in ' \t\r\n,':
                pos += 1
            if pos >= len(s):
                break
            if s[pos] == '}':
                pos += 1
                break
            val, pos = parse_value(s, pos)
            items.append(val)
        return items, pos
    elif c == '"':
        # Строка
        pos += 1
        start = pos
        while pos < len(s) and s[pos] != '"':
            if s[pos] == '\\':
                pos += 1
            pos += 1
        val = s[start:pos]
        pos += 1  # skip closing quote
        return val, pos
    else:
        # Число или UUID или другое
        start = pos
        while pos < len(s) and s[pos] not in ',} \t\r\n':
            pos += 1
        token = s[start:pos]
        # Попробовать число
        try:
            if re.match(r'^-?\d+$', token):
                return int(token), pos
            if re.match(r'^-?\d+\.\d+$', token):
                return float(token), pos
        except:
            pass
        return token, pos

def parse_payload(payload):
    """Парсит весь payload."""
    val, pos = parse_value(payload, 0)
    return val

def summarize(val, depth=0, max_depth=3):
    """Краткое резюме структуры."""
    indent = '  ' * depth
    if depth > max_depth:
        return indent + '...'
    if isinstance(val, list):
        lines = [indent + f'[{len(val)} items]']
        for i, item in enumerate(val[:20]):
            if isinstance(item, list):
                lines.append(summarize(item, depth+1, max_depth))
            elif isinstance(item, str) and len(item) > 60:
                lines.append(indent + f'  [{i}] str: {item[:60]}...')
            else:
                lines.append(indent + f'  [{i}] {repr(item)[:80]}')
        if len(val) > 20:
            lines.append(indent + f'  ... +{len(val)-20} more')
        return '\n'.join(lines)
    elif isinstance(val, str):
        if len(val) > 80:
            return indent + f'str: {val[:80]}...'
        return indent + f'str: {val}'
    else:
        return indent + repr(val)

def main():
    if len(sys.argv) < 2:
        print("Usage: parse_doxcel.py <file.mxl>")
        sys.exit(1)
    path = sys.argv[1]
    header, payload = read_doxcel(path)
    print(f"Header: {header}")
    print(f"Payload length: {len(payload)} chars")
    print(f"Payload first 200 chars: {payload[:200]}")
    print()
    try:
        val = parse_payload(payload)
        print("Parsed structure:")
        print(summarize(val, max_depth=2))
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
