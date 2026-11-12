---
description: "Active Directory: домен, OU, роли FSMO, диагностика dcdiag и repadmin, типовые проблемы с DNS и рассинхронизацией времени."
tags:
  - windows server
  - active directory
---

# Active Directory: основы

## Структура

```
Лес (Forest) contoso.local
└── Домен (Domain) contoso.local
    ├── OU=Users,DC=contoso,DC=local
    ├── OU=Computers,DC=contoso,DC=local
    └── OU=Servers,DC=contoso,DC=local
        └── OU=FileServers,DC=contoso,DC=local
```

- **Лес** — граница безопасности, общая схема и глобальный каталог.
- **Домен** — единая база учётных записей и политик.
- **OU** (подразделение) — контейнер для делегирования прав и применения GPO. Не путать с группами.
- **Сайт** (Site) — отражает физическую сеть, влияет на выбор контроллера домена клиентом.

## Контроллер домена

Роли FSMO — пять операций, которые нельзя реплицировать, их выполняет один DC:

| Роль | Область | За что отвечает |
|---|---|---|
| Schema Master | лес | изменения схемы |
| Domain Naming Master | лес | добавление/удаление доменов |
| PDC Emulator | домен | смена паролей, время, блокировки |
| RID Master | домен | выдача пулов RID |
| Infrastructure Master | домен | ссылки на объекты из других доменов |

Проверить, кто держит роли:

```powershell
netdom query fsmo
# или
Get-ADForest | Select-Object SchemaMaster, DomainNamingMaster
Get-ADDomain | Select-Object PDCEmulator, RIDMaster, InfrastructureMaster
```

## Диагностика

```powershell
dcdiag /v                      # полная проверка контроллера домена
dcdiag /test:dns /v            # отдельно DNS — самая частая причина проблем
repadmin /replsummary          # сводка по репликации
repadmin /showrepl             # подробно по партнёрам
repadmin /syncall /AdeP        # принудительная синхронизация
nltest /dsgetdc:contoso.local  # какой DC выберет клиент
```

## Пользователи и группы

```powershell
# создать пользователя
New-ADUser -Name "Иван Петров" -SamAccountName ipetrov `
  -UserPrincipalName ipetrov@contoso.local `
  -Path "OU=Users,DC=contoso,DC=local" `
  -AccountPassword (Read-Host -AsSecureString "Пароль") -Enabled $true

# разблокировать
Unlock-ADAccount -Identity ipetrov

# найти заблокированных
Search-ADAccount -LockedOut

# пароль истекает через 7 дней
Get-ADUser -Filter {Enabled -eq $true} -Properties PasswordLastSet |
  Where-Object { $_.PasswordLastSet -lt (Get-Date).AddDays(-83) }
```

## Грабли

!!! warning "Частые проблемы"
    - **DNS — 90 % проблем с AD.** Клиенты должны использовать в качестве DNS только контроллеры домена, а не роутер и не 8.8.8.8.
    - Время на DC и клиентах должно расходиться не более чем на 5 минут, иначе Kerberos не пустит.
    - Удаление OU удаляет всё содержимое — сначала проверьте `Get-ADObject -SearchBase ... -Recursive`.
    - Не переименовывайте домен «на всякий случай» — обратной операции нет.
