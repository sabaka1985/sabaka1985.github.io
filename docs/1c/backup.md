---
tags:
  - 1с
  - backup
---

# Резервное копирование 1С

## Способы

| Способ | Плюсы | Минусы |
|---|---|---|
| **Выгрузка `.dt`** средствами конфигуратора | консистентно, переносимо, не зависит от СУБД | долго на больших базах, блокировки |
| **Бэкап SQL-базы** (MS SQL / PostgreSQL) | быстро, штатными средствами | нужен доступ к СУБД |
| **Снимок ВМ** (hypervisor) | мгновенно | не заменяет логический бэкап |
| **Копия файловой базы** | просто | только при остановленной базе |

**Правило:** минимум один бэкап в день логическим способом + бэкап СУБД каждые 4–6 часов
для крупных баз + снимки ВМ как страховка.

## Выгрузка .dt из командной строки

```cmd
"C:\Program Files\1cv8\8.3.24.1548\bin\1cv8.exe" DESIGNER /F"C:\base1" /N"admin" /P"" ^
  /DumpIB"D:\backup\base1_2025-01-01.dt" /UC"КодРазрешения"
```

Для серверной базы вместо `/F` — `/S"server1\base1"`.

Восстановление:

```cmd
1cv8.exe DESIGNER /F"C:\base1" /N"admin" /P"" /RestoreIB"D:\backup\base1_2025-01-01.dt"
```

Или выгрузка/загрузка XML:

```cmd
1cv8.exe DESIGNER /F"C:\base1" /N"admin" /P"" /DumpConfigToFiles"D:\src" -Format Hierarchical
```

## Бэкап MS SQL

```sql
BACKUP DATABASE [base1]
TO DISK = N'D:\backup\base1_full.bak'
WITH INIT, COMPRESSION, CHECKSUM, STATS = 10;

BACKUP LOG [base1]
TO DISK = N'D:\backup\base1_log.trn'
WITH COMPRESSION, CHECKSUM;

RESTORE VERIFYONLY FROM DISK = N'D:\backup\base1_full.bak';
```

## Бэкап PostgreSQL

```bash
pg_dump -Fc -h localhost -U postgres base1 -f /backup/base1_$(date +%F).dump
pg_restore -h localhost -U postgres -d base1_restore /backup/base1_2025-01-01.dump
```

## Проверка бэкапа

!!! danger "Бэкап без проверки — не бэкап"
    Раз в месяц разворачивайте копию на тестовом сервере и проверяйте:

    1. база восстанавливается без ошибок;
    2. конфигурация открывается в конфигураторе;
    3. `Проверка и исправление` (`/CheckAndRepair`) проходит без ошибок;
    4. ключевые отчёты строятся.

## Хранение

- 3 копии, 2 носителя, 1 вне площадки (правило 3-2-1).
- Срок хранения: ежедневные — 2 недели, недельные — 2 месяца, месячные — год.
- Шифрование, если бэкап уезжает в облако.
- Мониторинг: размер файла и дата не меняются → алерт.
