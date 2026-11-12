---
tags:
  - windows server
  - active directory
---

# Windows Server

Инфраструктурные роли Windows: домен, политики, имена и адреса.

## Страницы раздела

| Страница | О чём |
|---|---|
| [Active Directory](ad.md) | домен, OU, FSMO, репликация, диагностика |
| [Групповые политики](gpo.md) | GPO, порядок применения, gpresult |
| [WMI-фильтры](wmi-filters.md) | справочник WQL-запросов для таргетинга GPO |
| [DNS и DHCP](dns-dhcp.md) | зоны, записи, области, резервирование |

## Часто нужные оснастки

| Задача | Оснастка / команда |
|---|---|
| Пользователи и компьютеры | `dsa.msc` |
| Сайты и службы | `dssite.msc` |
| Групповые политики | `gpmc.msc` |
| DNS | `dnsmgmt.msc` |
| DHCP | `dhcpmgmt.msc` |
| Просмотр событий | `eventvwr.msc` |
| Службы | `services.msc` |

## Быстрые команды

```powershell
Get-ADUser -Filter * -SearchBase "OU=Users,DC=contoso,DC=local"   # пользователи в OU
Get-ADComputer -Filter {Enabled -eq $true} | Measure-Object       # сколько ПК в домене
gpupdate /force                                                   # применить политики
gpresult /r                                                       # какие GPO применились
```

!!! note "Принцип"
    Всё, что можно автоматизировать в AD, автоматизируется через модуль `ActiveDirectory`
    в PowerShell. Оснастки — для разовых действий и визуальной проверки.
