# -*- coding: utf-8 -*-
"""Диагностика: расшифровать ключ Chrome вручную (pywin32 DPAPI) и проверить куки its.1c.ru."""
import os, sys, json, base64, sqlite3, shutil, tempfile

LOCAL_STATE = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State")
COOKIE_FILE = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies")
if not os.path.exists(COOKIE_FILE):
    COOKIE_FILE = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies")

def get_aes_key():
    with open(LOCAL_STATE, "r", encoding="utf-8") as f:
        ls = json.load(f)
    enc_key_b64 = ls["os_crypt"]["encrypted_key"]
    enc_key = base64.b64decode(enc_key_b64)
    assert enc_key[:5] == b"DPAPI", f"неожиданный префикс ключа: {enc_key[:5]!r}"
    dpapi_blob = enc_key[5:]
    import win32crypt
    aes_key = win32crypt.CryptUnprotectData(dpapi_blob, None, None, None, 0)[1]
    return aes_key

def main():
    print(f"Local State: {LOCAL_STATE}  exists={os.path.exists(LOCAL_STATE)}")
    print(f"Cookies:     {COOKIE_FILE}  exists={os.path.exists(COOKIE_FILE)}")
    if not (os.path.exists(LOCAL_STATE) and os.path.exists(COOKIE_FILE)):
        return 1

    aes_key = get_aes_key()
    print(f"[OK] AES-ключ получен, длина={len(aes_key)}")

    # Копируем БД куков (Chrome может держать её открытой)
    tmp = os.path.join(tempfile.gettempdir(), "chrome_cookies_copy.db")
    shutil.copy2(COOKIE_FILE, tmp)

    con = sqlite3.connect(tmp)
    cur = con.cursor()
    rows = cur.execute(
        "SELECT host_key, name, encrypted_value, path, is_secure FROM cookies "
        "WHERE host_key LIKE '%its.1c.ru%' OR host_key LIKE '%1c.ru%'"
    ).fetchall()
    print(f"\nКуков для 1c.ru: {len(rows)}")

    from Cryptodome.Cipher import AES
    ok = 0
    for host, name, enc_val, path, secure in rows:
        prefix = enc_val[:3].decode("latin1", "replace")
        body = enc_val[3:]
        val = None
        if prefix in ("v10", "v11"):
            try:
                iv, ct, tag = body[:12], body[12:-16], body[-16:]
                cipher = AES.new(aes_key, AES.MODE_GCM, iv=iv)
                val = cipher.decrypt_and_verify(ct, tag).decode("utf-8", "replace")
            except Exception as e:
                val = f"[decrypt FAIL: {type(e).__name__}]"
        else:
            val = f"[prefix={prefix} — не v10/v11, вероятно App-Bound Encryption]"
        shown = (val[:50] + "...") if val and len(val) > 50 else val
        print(f"  {host} | {name} = {shown}")
        if val and not val.startswith("["):
            ok += 1
    con.close()
    os.remove(tmp)
    print(f"\nРасшифровано: {ok}/{len(rows)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
