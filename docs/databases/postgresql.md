---
tags:
  - базы данных
  - postgresql
---

# PostgreSQL

## Бэкапы

```bash
# логический дамп (лучший выбор для переноса и небольших баз)
pg_dump -Fc -h localhost -U postgres mydb -f /backup/mydb_$(date +%F).dump

# только схема
pg_dump -s -h localhost -U postgres mydb -f schema.sql

# все базы сразу
pg_dumpall -U postgres -f /backup/all_$(date +%F).sql

# восстановление
pg_restore -h localhost -U postgres -d mydb_new -j 4 /backup/mydb_2025-01-01.dump
```

**Физический бэкап** для больших баз — `pg_basebackup` + WAL-архивирование:

```bash
pg_basebackup -h localhost -U replicator -D /backup/base -Ft -z -P
```

## Подключение и осмотр

```bash
psql -h localhost -U postgres -d mydb
```

```sql
\l                     -- список баз
\dt                    -- таблицы
\d+ orders             -- структура таблицы
\du                    -- роли
\df                    -- функции
\q                     -- выход
```

## Активность и блокировки

```sql
-- кто что делает
SELECT pid, usename, state, wait_event_type, wait_event,
       now() - query_start AS duration, left(query, 80) AS query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY duration DESC;

-- блокировки
SELECT blocked.pid AS blocked_pid, blocking.pid AS blocking_pid,
       left(blocked.query, 60) AS blocked_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
  ON blocking.pid = ANY(pg_blocking_pids(blocked.pid));

-- прибить зависший запрос
SELECT pg_terminate_backend(12345);
```

## Обслуживание

```sql
VACUUM (ANALYZE, VERBOSE) orders;   -- сборка мусора + статистика
VACUUM FULL orders;                 -- переписывает таблицу, блокирует!
REINDEX TABLE orders;

-- кто раздулся
SELECT relname, n_live_tup, n_dead_tup,
       pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```

`autovacuum` включён по умолчанию — не отключайте, только настраивайте пороги
для больших таблиц (`autovacuum_vacuum_scale_factor`).

## Пользователи и права

```sql
CREATE ROLE app LOGIN PASSWORD 'strong-password';
GRANT CONNECT ON DATABASE mydb TO app;
GRANT USAGE ON SCHEMA public TO app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app;
```

## Настройки, которые обычно меняют

| Параметр | Зачем |
|---|---|
| `shared_buffers` | ~25 % RAM |
| `effective_cache_size` | ~50–75 % RAM |
| `work_mem` | под сортировки на запрос, осторожно с большим числом соединений |
| `maintenance_work_mem` | для VACUUM и индексов |
| `max_connections` | лучше пул соединений (pgbouncer), чем много соединений |

Пути: `postgresql.conf`, `pg_hba.conf` (доступ по IP/паролю) — в Debian/Ubuntu `/etc/postgresql/<ver>/main/`.

## Грабли

!!! warning "Частое"
    - **`FATAL: no pg_hba.conf entry`** — не прописан клиент в `pg_hba.conf`.
    - **Долгие транзакции в `idle in transaction`** держат VACUUM и раздувают таблицы.
    - **`VACUUM FULL`** на живой базе блокирует таблицу — используйте `pg_repack`.
    - **Восстановление дампа в существующую базу** — конфликты объектов; создавайте пустую.
    - **Кодировка** при переносе: проверяйте `ENCODING` базы, иначе кириллица превращается в мусор.
