---
description: "Базовая настройка коммутатора Cisco: hostname, пароли, management IP, SSH вместо telnet, сохранение конфигурации и типичные ошибки."
tags:
  - cisco
  - коммутация
---

# Базовая настройка коммутатора Cisco

## Минимальный набор

```cisco
enable
configure terminal

! имя устройства
hostname sw-floor2

! пароль на привилегированный режим (хеш)
enable secret StrongPass123

! локальный пользователь для SSH
username admin privilege 15 secret AnotherPass456

! домен нужен для генерации RSA-ключа
ip domain-name contoso.local

! management IP на VLAN 1 (лучше — отдельный VLAN)
interface vlan 1
 ip address 192.168.10.5 255.255.255.0
 no shutdown
exit

! шлюз по умолчанию
ip default-gateway 192.168.10.1

! SSH вместо telnet
crypto key generate rsa modulus 2048
line vty 0 4
 transport input ssh
 login local
exit

! защита консоли
line con 0
 password ConsolePass789
 login
 logging synchronous
exit

! отключаем неиспользуемые порты (пример)
interface range gi0/10-24
 shutdown
exit

! сохранить
end
copy running-config startup-config
```

## Проверка

```cisco
show ip interface brief          ! адреса и статус портов
show running-config | section line vty
show users                        ! кто подключён
show ssh
ping 192.168.10.1
show interfaces status
```

## Пароли: что использовать

| Команда | Где хранится | Вид в конфиге |
|---|---|---|
| `enable secret` | хеш (тип 8/9/5) | `enable secret 9 $...` |
| `enable password` | открытый текст или слабый тип 7 | не использовать |
| `username ... secret` | хеш | безопасно |
| `service password-encryption` | тип 7 — обратимое «шифрование» | только для вида, не защита |

## Полезные мелочи

```cisco
! баннер
banner motd ^C
Authorized access only. Disconnect IMMEDIATELY if you are not an authorized user.
^C

! время и NTP
clock timezone MSK 3
ntp server 192.168.10.10

! журналирование на сервер
logging host 192.168.10.20
logging trap warnings

! резервная копия конфига на TFTP
copy running-config tftp:
```

## Грабли

!!! warning "Частое"
    - Забыли `no shutdown` на VLAN-интерфейсе — IP есть, связи нет.
    - SSH не поднимается: нет `ip domain-name` или RSA-ключ не сгенерирован (нужен 2048+).
    - `transport input ssh` без `login local` — не пустит вообще.
    - `enable password` вместо `enable secret` — пароль читается из конфига.
    - Не сохранён конфиг — после ребута всё вернулось «как было».
