---
tags:
  - windows server
  - gpo
  - wmi
  - справочник
---

# WMI-фильтры для групповых политик

WMI-фильтр — это условие на WQL-запросе, которое проверяется **на клиенте** перед применением
GPO. Политика достаётся компьютеру, только если запрос вернул хотя бы одну строку. Так одну
и ту же GPO можно нацелить на ноутбуки, на Windows 10, на ПК без нужного обновления и т. д.

## Как работает

1. Клиент получает список GPO, положенных ему по сайту, домену и OU.
2. Для каждой GPO с WMI-фильтром выполняется запрос к пространству имён `root\CIMv2`.
3. Запрос вернул результат — GPO применяется. Не вернул или WMI недоступен — GPO пропускается.

Что из этого следует:

- **Фильтр проверяется на компьютере**, даже если в GPO только пользовательские настройки —
  запросы про версию ОС, модель и диск работают, а «пользовательские» условия через WMI
  не сделать.
- **Фильтр один на всю GPO**, а не на отдельную настройку. Для точечного таргетинга отдельных
  пунктов используйте Item-level targeting в Preferences.
- **Каждый фильтр — это запрос к WMI при каждом применении политик**, то есть замедляет вход
  и обработку GPO. На сотнях машин с десятками фильтров это заметно.
- **Сломанный WMI = политика молча не применяется.** Проверяйте `gpresult` и службу Winmgmt.

## Как создать и применить

=== "Создать фильтр"

    1. `gpmc.msc` → в дереве домена найдите **WMI Filters** («WMI-фильтры»).
    2. Правый клик → **New**.
    3. Имя, описание, пространство имён `root\CIMv2`, язык запроса — WQL.
    4. Вставьте запрос → **Save**.

=== "Привязать к GPO"

    1. Откройте GPO → вкладка **Scope** («Область действия»).
    2. Внизу блок **WMI Filtering** → выберите фильтр из списка.
    3. Проверьте на клиенте:

    ```powershell
    gpupdate /force
    gpresult /r
    gpresult /h C:\temp\gpo.html
    ```

    В отчёте у отклонённых GPO будет указано, что не прошёл WMI-фильтр.

## Версии Windows и ProductType

Запросы почти всегда строятся на двух полях `Win32_OperatingSystem`.

| Поле | Значение |
|---|---|
| `Version` | `10.0%` — Windows 10 и 11, `6.3%` — 8.1 и Server 2012 R2, `6.2%` — 8 и Server 2012, `6.1%` — 7 и Server 2008 R2, `6.0%` — Vista и Server 2008, `5.2%` — Server 2003, `5.1%` — XP |
| `ProductType` | `1` — клиентская ОС, `2` — серверный контроллер домена, `3` — серверный не-DC |

`Windows 11` отвечает `10.0%`, поэтому отделить её от Windows 10 этим полем нельзя —
используйте `BuildNumber` (`>= 22000`) или `Caption`.

## Готовые запросы

### Операционная система

Клиентская Windows 7:

```sql
SELECT * FROM Win32_OperatingSystem WHERE Version LIKE "6.1%" AND ProductType = "1"
```

Серверная Windows Server 2008 R2 (включая контроллеры домена):

```sql
SELECT * FROM Win32_OperatingSystem
WHERE Version LIKE "6.1%" AND (ProductType = "2" OR ProductType = "3")
```

Клиентские Vista, 7, 8, 8.1:

```sql
SELECT * FROM Win32_OperatingSystem WHERE Version LIKE "6.%" AND ProductType = "1"
```

Только Windows Vista (клиентская, ветка 6.0):

```sql
SELECT Version, ProductType FROM Win32_OperatingSystem
WHERE Version >= "6.0" AND Version < "6.1" AND ProductType = "1"
```

Только серверные ОС, независимо от версии:

```sql
SELECT * FROM Win32_OperatingSystem WHERE Caption LIKE "%Server%"
```

64-битная архитектура:

```sql
SELECT * FROM Win32_OperatingSystem WHERE OSArchitecture = "64-bit"
```

Конкретная редакция по точному названию:

```sql
SELECT * FROM Win32_OperatingSystem WHERE Caption = "Microsoft Windows XP Professional"
```

Серверные редакции по `OperatingSystemSKU` (оператора `IN` в WQL нет — только цепочка `OR`):

```sql
SELECT OperatingSystemSKU FROM Win32_OperatingSystem
WHERE OperatingSystemSKU = 12 OR OperatingSystemSKU = 39 OR OperatingSystemSKU = 14
   OR OperatingSystemSKU = 41 OR OperatingSystemSKU = 13 OR OperatingSystemSKU = 40
   OR OperatingSystemSKU = 29
```

### Обновления и исправления

Windows XP Professional с пакетом обновления ниже SP3:

```sql
SELECT * FROM Win32_OperatingSystem
WHERE Caption = "Microsoft Windows XP Professional" AND ServicePackMajorVersion < 3
```

ПК с установленным обновлением KB921883:

```sql
SELECT * FROM Win32_QuickFixEngineering WHERE HotFixID = "KB921883"
```

Все установленные обновления (для проверки вручную):

```sql
SELECT * FROM Win32_QuickFixEngineering
```

### Железо и модель

Компьютеры Toshiba Tecra 800 и 810:

```sql
SELECT * FROM Win32_ComputerSystem
WHERE Manufacturer = "Toshiba" AND (Model = "Tecra 800" OR Model = "Tecra 810")
```

Компьютер по имени:

```sql
SELECT * FROM Win32_ComputerSystem WHERE Name = "PC-01" OR Name = "PC-02"
```

Компьютеры, в имени которых встречается фрагмент:

```sql
SELECT * FROM Win32_ComputerSystem WHERE Name LIKE "%бух%"
```

Диски с одним разделом или с числом секторов на дорожку больше 100:

```sql
SELECT * FROM Win32_DiskDrive WHERE Partitions < 2 OR SectorsPerTrack > 100
```

### Диски и файловая система

Свободно не менее 600 МБ на любом локальном диске:

```sql
SELECT * FROM Win32_LogicalDisk
WHERE FreeSpace > 629145600 AND Description <> "Network Connection"
```

На диске C: больше 1 ГБ:

```sql
SELECT * FROM Win32_LogicalDisk WHERE FreeSpace > 1073741824 AND Caption = "c:"
```

Диски C: или D: с NTFS и более 2 МБ свободного места:

```sql
SELECT * FROM Win32_LogicalDisk
WHERE (Name = "C:" OR Name = "D:") AND FreeSpace > 2000000 AND FileSystem = "NTFS"
```

Только диски с файловой системой:

```sql
SELECT * FROM Win32_LogicalDisk WHERE FileSystem IS NOT NULL
```

Диски без файловой системы (например, неразмеченные):

```sql
SELECT * FROM Win32_LogicalDisk WHERE FileSystem IS NULL
```

Диски с NTFS:

```sql
SELECT * FROM Win32_LogicalDisk WHERE FileSystem = "NTFS"
```

Сведения о дисках (для отладки запроса):

```sql
SELECT FreeSpace, DeviceID, Size, SystemName, Description FROM Win32_LogicalDisk
```

### Службы

Отключённые и не запущенные службы:

```sql
SELECT * FROM Win32_Service WHERE State = "Stopped" AND StartMode <> "Disabled"
```

### Журналы событий

Все события журнала «Приложение»:

```sql
SELECT * FROM Win32_NTLogEvent WHERE Logfile = "Application"
```

События журнала «Приложение» по источнику и дате:

```sql
SELECT * FROM Win32_NTLogEvent
WHERE LogFile = "Application"
  AND (SourceName = "SQLISService" OR SourceName = "SQLISPackage")
  AND TimeGenerated > "20050117"
```

### Установленное ПО

Office любой версии:

```sql
SELECT * FROM Win32_Product WHERE Name LIKE "Microsoft Office%"
```

Один из двух MSI-пакетов по имени:

```sql
SELECT * FROM Win32_Product WHERE Name = "MSIPackage1" OR Name = "MSIPackage2"
```

Продукт по идентификационному номеру:

```sql
SELECT * FROM Win32_Product WHERE IdentifyingNumber = "{5E076CF2-EFED-43A2-A623-13E0D62EC7E0}"
```

!!! warning "Win32_Product — осторожно"
    Перечисление `Win32_Product` заставляет MSI проверить и при необходимости
    «перенастроить» каждый установленный пакет: это медленно и может вызвать окна
    установщика у пользователя. Для поиска ПО лучше `Win32Reg_AddRemovePrograms`
    (если есть SCCM-клиент) или чтение ветки `Uninstall` в реестре через PowerShell.

### Компьютер в домене, сайт, время

Клиенты с именем сайта AD `Amsterdam`:

```sql
SELECT * FROM Win32_NTDomain WHERE ClientSiteName = "Amsterdam"
```

Часовой пояс `bias = -300` (UTC−5, восточное время США):

```sql
SELECT * FROM Win32_TimeZone WHERE Bias = -300
```

Текущий день недели — понедельник (`DayOfWeek = 1`):

```sql
SELECT DayOfWeek FROM Win32_LocalTime WHERE DayOfWeek = 1
```

Группы безопасности локального компьютера:

```sql
SELECT * FROM Win32_Group
```

Сетевые протоколы с поддержкой multicast:

```sql
SELECT * FROM Win32_NetworkProtocol WHERE SupportsMulticasting = TRUE
```

## Проверка запроса до публикации

Не привязывайте фильтр к GPO, не прогнав запрос на тестовой машине:

```powershell
Get-CimInstance -Namespace root/cimv2 -Query 'SELECT Caption, Version, ProductType, OSArchitecture FROM Win32_OperatingSystem' |
  Format-List Caption, Version, ProductType, OSArchitecture

# проверка конкретного условия
Get-CimInstance -Query 'SELECT * FROM Win32_LogicalDisk WHERE FileSystem = "NTFS"' |
  Select-Object DeviceID, FileSystem, @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,1)}}
```

Через старый `wmic` (есть не во всех новых сборках):

```cmd
wmic os get Caption,Version,ProductType /format:list
```

## Грабли

!!! warning "Частое"
    - **WMI-фильтр не заменяет Security Filtering.** Фильтр отбирает компьютеры, права —
      пользователей и группы. Работают они вместе.
    - **`LIKE` понимает только `%` и `_`**, а не `*` и `?`. Регистр в WQL обычно не важен,
      но `Caption` у редакций отличается (`Microsoft Windows Server 2012 R2 Standard`),
      поэтому `LIKE "%Server%"` надёжнее точного равенства.
    - **Запрос должен возвращать строки.** `WHERE 1=0` — валидный WQL, но политика не применится
      ни к кому; иногда так делают намеренно, чтобы «выключить» GPO без отвязки.
    - **Повреждённое хранилище WMI** (`winmgmt /verifyrepository`) — фильтры перестают
      срабатывать, а в `gpresult` GPO помечена как отфильтрованная. Лечится
      `winmgmt /salvagerepository` или пересборкой репозитория.
    - **Фильтры не работают на не-Windows клиентах** и на системах, где служба Winmgmt
      отключена политикой.
    - **`Win32_Product`** в фильтре — почти гарантированные тормоза на входе.
    - Один фильтр можно привязать ко многим GPO, но **нельзя** привязать несколько фильтров
      к одной GPO (логика ИЛИ делается внутри одного запроса).

## См. также

- [Групповые политики](gpo.md) — порядок применения, фильтрация, отчёты.
- [Active Directory](ad.md) — OU, сайты, диагностика домена.
