---
tags:
  - windows server
  - gpo
---

# Групповые политики (GPO)

## Как применяются

Порядок обработки — **LSDOU**:

1. **L**ocal — локальная политика компьютера;
2. **S**ite — политики сайта AD;
3. **D**omain — политики домена;
4. **O**U — политики подразделений, от родительского к дочернему.

Побеждает последняя применённая настройка. Исключения: **Enforced** (нельзя перебить),
**Block Inheritance** (запрет наследования), **Loopback** (для RDS/терминалов).

## Применение и проверка

```powershell
gpupdate /force                  # применить немедленно
gpupdate /force /boot            # с перезагрузкой (если требуется)
gpresult /r                      # какие GPO применились к пользователю и ПК
gpresult /h C:\temp\gpo.html     # полный отчёт в HTML — удобно разбирать
```

В отчёте смотрите разделы **Applied GPOs** и **Denied GPOs** — во втором указана причина
(фильтр безопасности, WMI-фильтр, отключена связь).

## Типовые задачи

=== "Пробросить сетевой диск"

    User Configuration → Preferences → Windows Settings → Drive Maps
    Action: Create, Location: `\\fs01\share`, Drive Letter: `S:`,
    Reconnect: включено.

=== "Политика паролей"

    Computer Configuration → Policies → Windows Settings → Security Settings →
    Account Policies → Password Policy. Действует на **домен**, если задана в
    Default Domain Policy, и на локальных пользователей — в остальных GPO.

=== "Запретить USB-накопители"

    Computer Configuration → Administrative Templates → System → Removable Storage Access →
    All Removable Storage classes: Deny all access = Enabled.

=== "Обновить настройки прокси"

    User Configuration → Preferences → Control Panel Settings → Internet Settings →
    Connections. Работает точечно, без перезагрузки.

## Фильтрация

- **Security Filtering** — кому применять (по умолчанию `Authenticated Users`).
- **WMI Filter** — применять только подходящим ПК, например ноутбукам:

```sql
SELECT * FROM Win32_ComputerSystem WHERE PCSystemType = 2
```

- **Item-level targeting** — внутри Preferences: по группе, OU, IP-диапазону.

## Грабли

!!! warning "Почему GPO «не работает»"
    1. ПК не в нужной OU или политика не прилинкована к ней.
    2. Отключён **Link Enabled** у самой связи.
    3. Пользователь/ПК не входит в Security Filtering.
    4. Настройка конфликтует с другой GPO, которая применяется позже.
    5. Политика компьютера не применилась до перезагрузки (не все настройки применяются на лету).
    6. Клиент не может достучаться до `\\contoso.local\SYSVOL` — проверьте доступность DC.

## Полезное

```powershell
Get-GPO -All | Select-Object DisplayName, GpoStatus, ModificationTime
Backup-GPO -All -Path D:\GPO-Backup                   # бэкап перед изменениями
Get-GPOReport -All -ReportType Html -Path C:\temp\all-gpo.html
```
