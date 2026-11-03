import json
import pymssql
from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.sse import SseServerTransport

app = FastAPI(title="1C MSSQL MCP Server")
mcp_server = Server("1c-mssql-server")

# Новая инициализация транспорта по правилам актуального SDK
sse = SseServerTransport("/mcp/messages")


import sys
import os
import pymssql

print("=== ENVIRONMENT ===")
print("Python:", sys.executable)
print("Version:", sys.version)
print("pymssql:", pymssql.__file__)
print("pymssql version:", pymssql.__version__)
print("Current dir:", os.getcwd())


# Настройки подключения к вашему SQL-серверу 1С
SQL_SERVER = "192.168.215.80"
SQL_USER = "Ai_user"
SQL_PASS = "__REDACTED__"
SQL_DB = "UT_TEST_22"
print("CONFIG:")
print(SQL_SERVER)
print(SQL_USER)
print(SQL_DB)
print(len(SQL_PASS))

print("=== SQL CONFIG ===")
print("SERVER:", SQL_SERVER)
print("USER:", SQL_USER)
print("DB:", SQL_DB)
print("PASS LENGTH:", len(SQL_PASS))

print("=== USERRRRRR ===")
import getpass
print("WINDOWS USER:", getpass.getuser())



import sys
import os
import pymssql

print("=== PROCESS INFO ===")
print(sys.executable)
print(os.getcwd())
print(pymssql.__file__)
print(pymssql.__version__)

print("=== DNS/IP TEST ===")
import socket
print(socket.gethostbyname("192.168.215.80"))




@mcp_server.list_tools()
async def handle_list_tools():
    return [Tool(
        name="execute_sql_query",
        description="Выполняет прямой SQL-запрос к базе данных 1С (UT_TEST_22). Используй INFORMATION_SCHEMA для поиска таблиц.",
        inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    )]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict):

    print("=== MCP TOOL CALL ===")
    print("NAME:", name)
    print("ARGS:", arguments)

    if name != "execute_sql_query":
        raise ValueError(f"Unknown tool: {name}")

    import pymssql

    conn = pymssql.connect(
        server="192.168.215.80",
        user="Ai_user",
        password="__REDACTED__",
        database="UT_TEST_22",
        login_timeout=10
    )

    cursor = conn.cursor(as_dict=True)

    query = arguments["query"]

    print("QUERY:")
    print(query)

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {
                    "rows": rows
                },
                ensure_ascii=False,
                default=str
            )
        )
    ]

# Эндпоинт для инициализации SSE-подключения (вход в комнату)
@app.get("/mcp/sse")
async def handle_sse_endpoint(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request.send) as (queue, write_sse):
        await sse.handle_post_message(mcp_server, queue, write_sse)


import subprocess

@app.get("/test-sql")
def test_sql():

    import pymssql

    conn = pymssql.connect(
        server="192.168.215.80",
        user="Ai_user",
        password="__REDACTED__",
        database="UT_TEST_22",
        login_timeout=10
    )

    return {"status":"OK"}
        
        
        
# Эндпоинт для отправки сообщений JSON-RPC
@app.post("/mcp/messages")
async def handle_mcp_message(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request.send)

if __name__ == "__main__":
    import uvicorn
    print("\n--- ЗАПУСК   MCP СЕРВЕРА 1С ---")
    uvicorn.run(app, host="0.0.0.0", port=5000)

 
    
@app.get("/test-sql")
async def test_sql():

    try:
        conn = pymssql.connect(
            server=SQL_SERVER,
            user=SQL_USER,
            password=SQL_PASS,
            database=SQL_DB
        )

        cursor = conn.cursor(as_dict=True)

        cursor.execute("""
        SELECT TOP 20
            name
        FROM sys.tables
        ORDER BY name
        """)

        rows = cursor.fetchall()

        conn.close()

        return {
            "status": "ok",
            "count": len(rows),
            "tables": rows
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
        
def execute_sql(query):

    conn = pymssql.connect(
        server=SQL_SERVER,
        user=SQL_USER,
        password=SQL_PASS,
        database=SQL_DB
    )

    cursor = conn.cursor(as_dict=True)

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    return rows


@app.get("/test-sql")
async def test_sql():

    try:

        rows = execute_sql(
            """
            SELECT TOP 10 name
            FROM sys.tables
            """
        )

        return {
            "status":"ok",
            "tables":rows
        }

    except Exception as e:

        import traceback
        traceback.print_exc()

        return {
            "status":"error",
            "message":repr(e)
        }
        
import asyncio


@app.get("/test-sql")
async def test_sql():

    loop = asyncio.get_event_loop()

    rows = await loop.run_in_executor(
        None,
        execute_sql,
        "SELECT TOP 10 name FROM sys.tables"
    )

    return {
        "tables":rows
    }

