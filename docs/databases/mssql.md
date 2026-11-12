---
description: "MS SQL Server: модели восстановления, бэкапы и восстановление на момент времени, индексы, обслуживание и диагностика запросов."
tags:
  - базы данных
  - mssql
---

# MS SQL Server

## Модели восстановления

| Модель | Что позволяет | Журнал |
|---|---|---|
| **Simple** | восстановление на момент бэкапа | обрезается автоматически |
| **Full** | на любой момент времени (point-in-time) | растёт, нужны бэкапы журнала |
| **Bulk-logged** | как Full, но минимальный лог для массовых операций | почти как Full |

Для продакшена с требованием «не терять данные» — **Full** + бэкап журнала каждые 15–60 минут.

## Бэкапы

```sql
-- полный
BACKUP DATABASE [base1] TO DISK = N'D:\backup\base1_full.bak'
WITH INIT, COMPRESSION, CHECKSUM, STATS = 5;

-- журнал
BACKUP LOG [base1] TO DISK = N'D:\backup\base1_log.trn'
WITH COMPRESSION, CHECKSUM;

-- дифференциальный
BACKUP DATABASE [base1] TO DISK = N'D:\backup\base1_diff.bak'
WITH DIFFERENTIAL, COMPRESSION;

-- проверка
RESTORE VERIFYONLY FROM DISK = N'D:\backup\base1_full.bak';
```

Восстановление на момент времени:

```sql
RESTORE DATABASE [base1] FROM DISK = N'D:\backup\base1_full.bak' WITH NORECOVERY;
RESTORE LOG [base1] FROM DISK = N'D:\backup\base1_log.trn' WITH NORECOVERY;
RESTORE LOG [base1] FROM DISK = N'D:\backup\base1_log2.trn'
WITH STOPAT = '2025-01-01T12:00:00', RECOVERY;
```

## Диагностика

```sql
-- активные запросы и ожидания
SELECT r.session_id, r.status, r.wait_type, r.wait_time, r.blocking_session_id,
       t.text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.session_id > 50;

-- топ по CPU
SELECT TOP 10 total_worker_time/execution_count AS avg_cpu, execution_count,
       SUBSTRING(t.text, 1, 200) AS query
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) t
ORDER BY total_worker_time DESC;

-- размер баз и свободное место в файлах
SELECT DB_NAME(database_id) AS db, name, size*8/1024 AS size_mb,
       CAST(FILEPROPERTY(name,'SpaceUsed')*8/1024 AS int) AS used_mb
FROM sys.master_files;
```

## Обслуживание

```sql
-- проверка целостности (по выходным, не в рабочее время)
DBCC CHECKDB('base1') WITH NO_INFOMSGS;

-- фрагментация и перестройка индексов
SELECT OBJECT_NAME(ps.object_id) AS tbl, i.name, ps.avg_fragmentation_in_percent
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
JOIN sys.indexes i ON i.object_id = ps.object_id AND i.index_id = ps.index_id
WHERE ps.avg_fragmentation_in_percent > 30;

ALTER INDEX ALL ON dbo.Orders REBUILD WITH (ONLINE = ON);

-- обновление статистики
UPDATE STATISTICS dbo.Orders WITH FULLSCAN;
```

## Грабли

!!! warning "Частое"
    - **Журнал растёт до диска** — модель Full, а бэкап журнала не настроен.
    - **`autogrow` мелкими шагами** — фрагментация и тормоза; ставьте шаг 1–4 ГБ.
    - **Файлы БД на диске C:** — место кончилось, сервер встал.
    - **Восстановление «на вчера»** без NORECOVERY по цепочке — не восстановится.
    - **`ONLINE = ON`** недоступен в Express-редакции.
