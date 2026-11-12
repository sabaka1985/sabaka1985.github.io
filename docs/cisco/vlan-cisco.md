---
tags:
  - cisco
  - vlan
  - коммутация
---

# VLAN на Cisco

## Создание VLAN

```cisco
configure terminal
vlan 10
 name USERS
vlan 20
 name VOICE
vlan 30
 name SERVERS
vlan 999
 name NATIVE
exit
```

## Порты доступа

```cisco
interface range gi0/1-9
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
exit
```

`portfast` — сразу переводит порт в forwarding (для ПК), `bpduguard` — защита от подключения чужого коммутатора.

## Trunk

```cisco
interface gi0/24
 description UPLINK-to-core
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30
 no shutdown
exit
```

## Голосовой VLAN

```cisco
interface gi0/5
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 spanning-tree portfast
exit
```

Телефон получает VLAN 20 по LLDP/CDP, ПК за телефоном остаётся в VLAN 10.

## Inter-VLAN routing

=== "На L3-коммутаторе (SVI)"

    ```cisco
    ip routing
    interface vlan 10
     ip address 192.168.10.1 255.255.255.0
     no shutdown
    exit
    interface vlan 20
     ip address 192.168.20.1 255.255.255.0
     no shutdown
    exit
    ```

=== "Router-on-a-stick"

    ```cisco
    interface gi0/0
     no shutdown
    exit
    interface gi0/0.10
     encapsulation dot1Q 10
     ip address 192.168.10.1 255.255.255.0
    exit
    interface gi0/0.20
     encapsulation dot1Q 20
     ip address 192.168.20.1 255.255.255.0
    exit
    ```

## VTP

VTP синхронизирует список VLAN между коммутаторами, но легко «размножает» ошибку на всю сеть.

- **VTP transparent** — самый предсказуемый режим, VLAN создаются вручную на каждом устройстве.
- **VTP server/client** — удобно в большой сети, но требует аккуратности с ревизией и доменом.

```cisco
vtp mode transparent
vtp domain CONTOSO
```

## Проверка

```cisco
show vlan brief
show vlan id 10
show interfaces trunk
show interfaces gi0/24 switchport
show spanning-tree vlan 10
show mac address-table vlan 10
```

## Грабли

!!! warning "Частое"
    - **VLAN не разрешён в trunk** (`allowed vlan`) — трафик молча отбрасывается.
    - **Native VLAN не совпадает** — STP-петли и «переезд» трафика в чужой VLAN.
    - **VTP-ревизия** с более высоким номером затирает VLAN на всём домене.
    - **SVI down/down**, потому что ни один порт в этом VLAN не активен — это норма, добавьте порт.
    - Между VLAN нет маршрута — проверьте `show ip route` и `ip routing`.
