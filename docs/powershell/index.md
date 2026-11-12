---
tags:
  - powershell
---

# PowerShell

Автоматизация Windows: от командлетов до готовых скриптов для админа.

## Страницы раздела

| Страница | О чём |
|---|---|
| [Основы](basics.md) | командлеты, объекты, пайплайн, переменные |
| [Готовые скрипты](scripts.md) | AD, диск, службы, отчёты |

## Три правила

1. **PowerShell работает с объектами, а не с текстом.** `Get-Process` возвращает объекты со свойствами.
2. **Пайплайн (`|`)** передаёт объект дальше по цепочке.
3. **Проверяйте, что делает команда:** `-WhatIf` и `-Confirm` для опасных операций.

## Быстрый старт

```powershell
Get-Help Get-ADUser -Examples      # справка с примерами
Get-Command *service*              # найти команду
Get-Member                         # какие свойства и методы у объекта
$PSVersionTable                    # версия PowerShell
Get-ExecutionPolicy -List          # политика запуска скриптов
```

## Полезные однострочники

```powershell
Get-Service | Where-Object Status -eq 'Stopped' | Select-Object Name, DisplayName
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WS
Get-ChildItem C:\Logs -Recurse -Filter *.log | Measure-Object Length -Sum
Get-EventLog -LogName System -EntryType Error -Newest 20
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,1)}}
```
