@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict):

    print("=== MCP TOOL CALL ===")
    print(name)
    print(arguments)

    if name != "execute_sql_query":
        raise ValueError("Unknown tool")


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