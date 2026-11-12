---
tags:
  - сети
  - коммутация
---

# VLAN и trunk

## VLAN — зачем

VLAN (Virtual LAN) режет один физический коммутатор на несколько независимых
широковещательных доменов. Плюсы:

- меньше широковещательного трафика;
- безопасность: бухгалтерия не видит гостевую сеть;
- гибкость: устройства в одном VLAN могут стоять в разных кабинетах;
- меньше кабеля — один trunk вместо десяти проводов между этажами.

## Access и trunk

| Режим порта | Что делает | Куда включать |
|---|---|---|
| **Access** | кадры одного VLAN без тега | ПК, принтер, камера |
| **Trunk** | несколько VLAN, кадры с тегом 802.1Q | связь коммутатор ↔ коммутатор, коммутатор ↔ роутер |

Тег 802.1Q — 4 байта в кадре Ethernet, внутри число VLAN (VID 1–4094).
Кадр без тега, пришедший в trunk, попадает в **native VLAN** (по умолчанию VLAN 1).

## Пример (Cisco)

```cisco
! создаём VLAN
Switch(config)# vlan 10
Switch(config-vlan)# name USERS
Switch(config)# vlan 20
Switch(config-vlan)# name VOICE

! порт доступа
Switch(config)# interface gi0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10

! порт в trunk
Switch(config)# interface gi0/24
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20
Switch(config-if)# switchport trunk native vlan 999
```

## Проверка

```cisco
show vlan brief                 # VLAN и порты в них
show interfaces trunk           # какие порты в trunk, какие VLAN разрешены
show interfaces gi0/24 switchport
```

## Грабли

!!! warning "Типовые ошибки"
    - **Native VLAN не совпадает** на двух концах trunk — трафик «прыгает» в чужой VLAN, STP может ругаться.
    - **VLAN не создан** на транзитном коммутаторе — trunk пропустит его только если разрешён явно; иначе кадры молча отбрасываются.
    - **VLAN 1 как рабочий** — плохая практика: используйте его только как native/служебный.
    - **Access вместо trunk** на линке между коммутаторами — работать будет только один VLAN.

## Межвлановый трафик

Между VLAN по умолчанию **нет** связи. Нужен маршрутизатор:

- **Router-on-a-stick** — на роутере саб-интерфейсы (`encapsulation dot1q 10`);
- **L3-коммутатор** — `interface vlan 10` + `ip routing`.
