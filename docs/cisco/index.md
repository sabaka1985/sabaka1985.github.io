---
tags:
  - cisco
---

# Cisco

Настройка оборудования Cisco: коммутаторы, VLAN, базовая безопасность, диагностика.

## Страницы раздела

| Страница | О чём |
|---|---|
| [Базовая настройка коммутатора](switch-setup.md) | имя, пароли, management IP, SSH |
| [VLAN на Cisco](vlan-cisco.md) | VLAN, trunk, inter-VLAN routing, проверка |

## Режимы CLI

| Режим | Приглашение | Как попасть |
|---|---|---|
| Пользовательский | `Switch>` | по умолчанию |
| Привилегированный | `Switch#` | `enable` |
| Глобальной конфигурации | `Switch(config)#` | `configure terminal` |
| Интерфейса | `Switch(config-if)#` | `interface gi0/1` |
| Линии | `Switch(config-line)#` | `line vty 0 4` |

Выход: `exit` — на уровень выше, `end` — сразу в привилегированный.

## Полезные команды

```cisco
show version
show running-config
show ip interface brief
show mac address-table
show cdp neighbors
show logging
show interfaces status
copy running-config startup-config
```

!!! note "Правило"
    Всё, что не сохранено через `copy running-config startup-config` (или `write memory`),
    исчезнет после перезагрузки. Сохраняйте конфиг после каждого осмысленного изменения.
