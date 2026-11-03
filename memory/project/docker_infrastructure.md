---
name: Docker infrastructure and SSH access
description: Docker compose setup, SSH credentials for ntmz, DuckDB containers with ports
type: reference
---

## Qwen CLI Docker Compose

- **Path**: `C:\AI_PROJECTS\Qwen_CLI` — содержит docker-compose конфигурацию для Docker-версии Qwen Code

## SSH Access to ntmz

- **Host**: `root@192.168.215.174`
- **Port**: 2222
- **Password**: `__REDACTED__`
- **Contents**: Multiple Qwen Code instances and project history

## DuckDB Docker Containers

| Container ID | Image | Port Mapping |
|---|---|---|
| `2fddc646f389` | `duckdb_ai_core:backup` | 5002:5002 |
| `76c69ce300e9` | `duckdb_ai_mcp:backup` | 5001:5001 |
