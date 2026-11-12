---
tags:
  - powershell
  - основы
---

# Основы PowerShell

## Командлеты

Формат: `Глагол-Существительное` — `Get-Service`, `Set-Item`, `New-ADUser`, `Remove-Item`.

Основные глаголы: `Get`, `Set`, `New`, `Remove`, `Start`, `Stop`, `Test`, `Import`, `Export`.

```powershell
Get-Command -Verb Get -Noun *Service   # найти все Get-*Service
Get-Help Get-Service -Full             # подробная справка
Get-Help about_Arrays                  # концептуальная справка
```

## Объекты и пайплайн

```powershell
Get-Service | Where-Object { $_.Status -eq 'Running' } |
  Select-Object Name, DisplayName |
  Sort-Object Name |
  Format-Table -AutoSize
```

- `$_` — текущий объект в пайплайне.
- `Where-Object` — фильтр, `Select-Object` — выбор свойств, `Sort-Object` — сортировка.
- `ForEach-Object` — действие над каждым объектом.

Вычисляемые свойства:

```powershell
Get-Process | Select-Object Name,
  @{Name='RAM_MB'; Expression={[math]::Round($_.WorkingSet64/1MB,1)}}
```

## Переменные и типы

```powershell
$name = "server01"
$count = 42
$list = @("a","b","c")            # массив
$empty = @()                      # пустой массив для накопления
$map = @{ Key = "Value"; N = 1 }  # хеш-таблица
$list += "d"                      # добавление (медленно в цикле — используйте List)
```

Строки:

```powershell
"Сервер: $name"                          # интерполяция
"Путь: $($env:TEMP)\log.txt"             # выражение внутри строки
"Строка {0} и {1}" -f $name, $count      # форматирование
```

## Условия и циклы

```powershell
if ($count -gt 10) { "много" } elseif ($count -gt 0) { "немного" } else { "ноль" }

foreach ($item in $list) { Write-Output $item }

for ($i = 0; $i -lt 5; $i++) { Write-Output $i }

while ($true) { break }

switch ($name) {
  "server01" { "основной" }
  default    { "неизвестный" }
}
```

Сравнения: `-eq -ne -gt -lt -ge -le -like -match -contains -in`.

## Функции

```powershell
function Get-FreeSpace {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ComputerName,
        [int]$ThresholdGB = 10
    )
    $disks = Get-CimInstance Win32_LogicalDisk -ComputerName $ComputerName -Filter "DriveType=3"
    foreach ($d in $disks) {
        [pscustomobject]@{
            Computer = $ComputerName
            Drive    = $d.DeviceID
            FreeGB   = [math]::Round($d.FreeSpace/1GB, 1)
            Low      = ([math]::Round($d.FreeSpace/1GB, 1) -lt $ThresholdGB)
        }
    }
}
```

## Ошибки

```powershell
try {
    Get-Item "C:\no-such-file" -ErrorAction Stop
}
catch {
    Write-Error "Не удалось: $($_.Exception.Message)"
}
finally {
    Write-Verbose "Завершено"
}
```

- `-ErrorAction Stop` — превратить некритичную ошибку в исключение.
- `$ErrorActionPreference = 'Stop'` — в начале скрипта для строгого режима.

## Ввод-вывод

```powershell
Get-Content .\log.txt -Tail 50 -Wait      # следить за файлом
"текст" | Out-File .\out.txt -Encoding utf8
Get-ChildItem | Export-Csv .\list.csv -NoTypeInformation -Encoding UTF8
$data = Import-Csv .\list.csv
```

## Транскрипт и логирование

```powershell
Start-Transcript -Path .\session.txt
# ... работа ...
Stop-Transcript
```

!!! tip "Совет"
    `Get-Help <команда> -Online` открывает актуальную документацию в браузере —
    быстрее, чем искать в интернете вручную.
