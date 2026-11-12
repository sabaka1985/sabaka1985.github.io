---
tags:
  - powershell
  - скрипты
---

# Готовые скрипты

## Свободное место на всех серверах

```powershell
$servers = Get-Content .\servers.txt
$report = foreach ($s in $servers) {
    Get-CimInstance Win32_LogicalDisk -ComputerName $s -Filter "DriveType=3" -ErrorAction SilentlyContinue |
        ForEach-Object {
            [pscustomobject]@{
                Server = $s
                Drive  = $_.DeviceID
                FreeGB = [math]::Round($_.FreeSpace/1GB,1)
                TotalGB = [math]::Round($_.Size/1GB,1)
                Percent = [math]::Round($_.FreeSpace/$_.Size*100,1)
            }
        }
}
$report | Sort-Object Percent | Export-Csv .\disk-report.csv -NoTypeInformation -Encoding UTF8
```

## Учётные записи AD с истекающим паролем

```powershell
Import-Module ActiveDirectory
$days = 7
Get-ADUser -Filter {Enabled -eq $true -and PasswordNeverExpires -eq $false} `
  -Properties PasswordLastSet, PasswordExpires, EmailAddress |
  Where-Object { $_.PasswordExpires -ne $null -and $_.PasswordExpires -lt (Get-Date).AddDays($days) } |
  Select-Object Name, SamAccountName, EmailAddress, PasswordExpires |
  Sort-Object PasswordExpires |
  Export-Csv .\expiring.csv -NoTypeInformation -Encoding UTF8
```

## Массовый сброс пароля с уведомлением

```powershell
$users = Import-Csv .\users.csv      # колонки: SamAccountName, Email
foreach ($u in $users) {
    $new = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 12 | ForEach-Object { [char]$_ })
    Set-ADAccountPassword -Identity $u.SamAccountName -Reset -NewPassword (ConvertTo-SecureString $new -AsPlainText -Force)
    Set-ADUser -Identity $u.SamAccountName -ChangePasswordAtLogon $true
    Send-MailMessage -To $u.Email -From "admin@contoso.local" `
      -Subject "Новый пароль" -Body "Ваш новый пароль: $new" `
      -SmtpServer "smtp.contoso.local"
}
```

## Отчёт по службам, которые должны работать

```powershell
$servers = @("dc01","fs01","sql01")
$mustRun = @("DNS","DHCPServer","LanmanServer","WinRM")
foreach ($s in $servers) {
    foreach ($svc in $mustRun) {
        $srv = Get-Service -ComputerName $s -Name $svc -ErrorAction SilentlyContinue
        if ($null -eq $srv) { continue }
        if ($srv.Status -ne "Running") {
            [pscustomobject]@{ Server=$s; Service=$svc; Status=$srv.Status }
        }
    }
}
```

## Поиск крупных файлов на диске

```powershell
Get-ChildItem C:\ -Recurse -File -ErrorAction SilentlyContinue |
  Sort-Object Length -Descending |
  Select-Object -First 20 FullName, @{n='SizeMB';e={[math]::Round($_.Length/1MB,1)}}
```

## Резервное копирование GPO

```powershell
$stamp = Get-Date -Format "yyyy-MM-dd"
New-Item -ItemType Directory -Force -Path "D:\GPO-Backup\$stamp" | Out-Null
Backup-GPO -All -Path "D:\GPO-Backup\$stamp"
```

## Проверка доступности портов

```powershell
$targets = @(
  @{Host="dc01"; Port=389},
  @{Host="fs01"; Port=445},
  @{Host="sql01"; Port=1433}
)
foreach ($t in $targets) {
    $ok = Test-NetConnection -ComputerName $t.Host -Port $t.Port -InformationLevel Quiet -WarningAction SilentlyContinue
    "{0}:{1} — {2}" -f $t.Host, $t.Port, $(if ($ok) {"OK"} else {"НЕДОСТУПЕН"})
}
```

!!! tip "Как запускать"
    Сохраните в `.ps1` и запускайте `powershell.exe -ExecutionPolicy Bypass -File .\script.ps1`.
    Для регулярных задач — Планировщик заданий с учётной записью службы.
