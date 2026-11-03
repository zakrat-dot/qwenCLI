import pymssql
import traceback
import sys
import os
from fastapi import FastAPI

import uvicorn


# =========================
# SQL CONFIG
# =========================

SQL_SERVER = "192.168.215.80"
SQL_USER = "Ai_User"
SQL_PASS = "__REDACTED__"
SQL_DB = "UT_TEST_22"


print("=== ENVIRONMENT ===")
print("Python:", sys.executable)
print("pymssql:", pymssql.__file__)
print("Current dir:", os.getcwd())

print("=== SQL CONFIG ===")
print(SQL_SERVER)
print(SQL_USER)
print(SQL_DB)
print("PASS LENGTH:", len(SQL_PASS))


# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="1C SQL Test Server"
)


# =========================
# SQL FUNCTION
# =========================

def execute_sql(query):

    print("START SQL CONNECT")

    conn = pymssql.connect(
        server=SQL_SERVER,
        user=SQL_USER,
        password=SQL_PASS,
        database=SQL_DB,
        login_timeout=10
    )

    print("SQL CONNECT OK")

    cursor = conn.cursor(as_dict=True)

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    print("SQL CLOSED")

    return rows



# =========================
# TEST ENDPOINT
# =========================

@app.get("/test-sql")
def test_sql():

    try:

        result = execute_sql(
            """
            SELECT TOP 10
                name
            FROM sys.tables
            ORDER BY name
            """
        )


        return {
            "status":"ok",
            "count":len(result),
            "tables":result
        }


    except Exception as e:

        print("ERROR")
        traceback.print_exc()

        return {
            "status":"error",
            "message":repr(e)
        }



# =========================
# START
# =========================

if __name__ == "__main__":

    print("")
    print("--- START FASTAPI SQL TEST ---")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000
    )