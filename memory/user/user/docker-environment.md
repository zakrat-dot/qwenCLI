---
name: Qwen работает в Docker контейнере qwen_terminal на сети ai-net
description: Qwen запущен в Docker, не на хосте. Docker CLI недоступен, доступ к соседним контейнерам через Docker DNS по имени контейнера
type: user
---

Qwen работает внутри Docker-контейнера `qwen_terminal` (IP 172.18.0.4) на внешней Docker-сети `ai-net`.

- Docker CLI недоступен внутри контейнера
- Соседние контейнеры доступны по имени через Docker DNS (`127.0.0.11`)
- Для проверки доступности сервиса: TCP-скан по имени контейнера + порт
- Хост-машина доступна через `host.docker.internal` (если включено)
