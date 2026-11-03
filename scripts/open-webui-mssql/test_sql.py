import pymssql
import sys
import os
import pymssql

print("=== ENVIRONMENT ===")
print("Python:", sys.executable)
print("Version:", sys.version)
print("pymssql:", pymssql.__file__)
print("pymssql version:", pymssql.__version__)
print("Current dir:", os.getcwd())



server="192.168.215.80"
user="Ai_user"
password="__REDACTED__"
database="UT_TEST_22"

import pymssql
import socket
import sys
import os

print("=== ENVIRONMENT ===")
print("Python:", sys.executable)
print("Version:", sys.version)
print("pymssql:", pymssql.__file__)
print("Current dir:", os.getcwd())


server = "192.168.215.80"
user = "Ai_user"
password = "__REDACTED__"
database = "UT_TEST_22"


try:
    print("=== TCP TEST ===")

    sock = socket.create_connection(
        (server, 1433),
        timeout=5
    )

    print("TCP OK")

    sock.close()


    print("=== SQL TEST ===")

    conn = pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        login_timeout=10
    )

    print("CONNECT OK")


    cursor = conn.cursor()

    cursor.execute("SELECT TOP 10 FileName FROM dbo.Files")

    print(cursor.fetchone())


    conn.close()


except Exception as e:
    print("ERROR:")
    print(repr(e))