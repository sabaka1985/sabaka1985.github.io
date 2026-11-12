---
tags:
  - траблшутинг
  - windows
---

# Проблемы Windows

## Компьютер не входит в домен / «доверительные отношения не установлены»

Причина: пароль компьютерной учётной записи в AD и на ПК разошлись
(восстановление из бэкапа, откат снимка ВМ, долгое отсутствие в сети).

```powershell
# на проблемном ПК от администратора
Test-ComputerSecureChannel -Verbose            # покажет состояние канала
Test-ComputerSecureChannel -Repair -Credential (Get-Credential)  # исправить
Reset-ComputerMachinePassword -Credential (Get-Credential)
Restart-Computer
```

Если не помогло — вывести из домена и ввести заново (с сохранением профиля пользователя:
профиль не удаляется, если не чистить реестр `ProfileList`).

## Применение GPO и политик

```cmd
gpupdate /force
gpresult /r
gpresult /h %TEMP%\gpo.html && start %TEMP%\gpo.html
rsop.msc                 :: итоговая политика (устаревшая, но наглядная)
```

Смотрите **Denied GPOs** — там написана причина отказа.

## Медленно работает ПК

```powershell
# топ по CPU и памяти
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WS
Get-Process | Sort-Object WS  -Descending | Select-Object -First 10 Name, CPU, WS

# автозагрузка
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location

# состояние диска
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus
Get-Volume | Select-Object DriveLetter, FileSystemLabel, @{n='FreeGB';e={[math]::Round($_.SizeRemaining/1GB,1)}}

# журнал ошибок за сутки
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-1)} |
  Select-Object TimeCreated, Id, ProviderName, Message -First 30
```

## Служба не запускается

1. `services.msc` → вкладка **Зависимости** — запущены ли зависимые службы.
2. Просмотр событий → **Система** и **Приложение** — код ошибки в момент старта.
3. Права учётной записи службы и доступ к каталогам.
4. Проверить, не занят ли порт: `netstat -ano | findstr :80`.

## Не открывается сетевой ресурс

```powershell
Test-NetConnection fs01 -Port 445
net use \\fs01\share /user:CONTOSO\ivan
klist purge                     # сброс кэша Kerberos после смены прав
```

Типичные причины: нет прав NTFS, нет прав на общий ресурс (share permissions),
не совпали учётные данные, включена гостевая аутентификация, блокирует файрвол.

## Обновления и перезагрузка

```cmd
:: посмотреть установленные обновления
wmic qfe list brief /format:table
:: отложенные перезагрузки
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"
```

## Забыт пароль локального администратора

- Сброс через установочный носитель и `utilman.exe` → `cmd.exe` — рабочий, но грубый способ; делать только на своей машине.
- Лучше заранее иметь локальную учётную запись восстановления (LAPS).
- В домене — сброс через AD, вход по кэшированным учётным данным не поможет после сброса.

## Полезные логи

| Лог | Что смотреть |
|---|---|
| `System` | драйверы, службы, диск |
| `Application` | приложения |
| `Security` | вход/выход, 4624/4625, 4740 (блокировка) |
| `Microsoft-Windows-GroupPolicy/Operational` | ошибки применения GPO |
| `Microsoft-Windows-Sysmon/Operational` | если установлен Sysmon |

```powershell
Get-WinEvent -LogName Security -MaxEvents 50 |
  Where-Object Id -in 4624,4625,4740 |
  Select-Object TimeCreated, Id, Message
```

!!! tip "Быстрая зацепка"
    Если проблема воспроизводится у всех — смотрите сервер (DC, DNS, файловый, SQL).
    Если у одного — смотрите клиента (профиль, кэш, GPO, права). Это сразу вдвое сужает поиск.
