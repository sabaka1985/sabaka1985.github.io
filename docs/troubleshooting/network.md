---
description: "Диагностика сети по шагам: ping, трассировка, DNS, проверка портов, tcpdump и pktmon, разбор типовых симптомов."
tags:
  - траблшутинг
  - сети
---

# Диагностика сети

## Порядок проверки

```
кабель / Wi-Fi
   ↓ ping шлюза
   ↓ ping 8.8.8.8
   ↓ ping по имени (DNS)
   ↓ проверка порта (telnet / Test-NetConnection)
   ↓ приложение
```

Каждый шаг отвечает на свой вопрос. Если ping шлюза не идёт — дальше смотреть нет смысла.

## Windows

```cmd
ipconfig /all                     :: адрес, шлюз, DNS, DHCP
ipconfig /flushdns                :: сброс кэша DNS
ipconfig /release && ipconfig /renew
ping -t 8.8.8.8                   :: непрерывный ping (Ctrl+C)
ping -n 20 -l 1400 8.8.8.8       :: проверка MTU/потерь
tracert -d ya.ru                  :: маршрут без резолва имён
nslookup ya.ru 8.8.8.8            :: DNS-запрос к конкретному серверу
netstat -ano | findstr :443       :: кто слушает порт
route print                       :: таблица маршрутов
arp -a                            :: таблица ARP
```

## Linux

```bash
ip a; ip r
ping -c 4 8.8.8.8
traceroute -n ya.ru
dig ya.ru +short
dig @8.8.8.8 ya.ru
ss -tulpn | grep 443
sudo tcpdump -i eth0 -nn port 443 -c 20
mtr -n ya.ru                      # трассировка + потери в реальном времени
```

## PowerShell

```powershell
Test-NetConnection ya.ru -Port 443
Test-NetConnection 192.168.10.20 -Port 3389 -InformationLevel Detailed
Resolve-DnsName ya.ru
Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection -LocalPort 443
```

## Что означают симптомы

| Симптом | Возможная причина |
|---|---|
| `Request timed out` на шлюз | не тот VLAN, порт в `shutdown`, неверная маска |
| Пинг идёт, но с потерями | плохой кабель/коннектор, дуплекс, помехи Wi-Fi |
| `Destination host unreachable` | нет маршрута, неверный шлюз |
| Разрешение имён не работает | DNS-сервер недоступен, неверная зона |
| Порт закрыт | служба не запущена, файрвол, ACL |
| Работает по IP, не по имени | DNS или запись в hosts |
| Соединение есть, но TLS-ошибка | сертификат, время на клиенте, SNI |

## Частые сетевые проблемы

!!! warning "MTU и VPN"
    Через VPN часто «ломаются» только крупные пакеты (сайты грузятся частично).
    Проверка: `ping -f -l 1472 8.8.8.8` (Windows) — если фрагментация не проходит при размере
    меньше 1472, уменьшайте MTU. Типичное решение — MTU 1400 на VPN-интерфейсе.

!!! warning "DHCP"
    `169.254.x.x` (APIPA) → адрес не получен. Причины: DHCP-сервер недоступен,
    в VLAN нет релея, пул исчерпан, порт в неправильном VLAN.

!!! warning "Дубликат IP"
    Конфликт адресов: в логах коммутатора `%IP-4-DUPADDR`, у пользователей «сеть есть, но не работает».
    Решается резервированием адресов на DHCP и проверкой статических настроек.

## Захват трафика

```bash
# Linux: сохранить 200 пакетов по порту 443
sudo tcpdump -i eth0 -nn port 443 -c 200 -w /tmp/cap.pcap

# фильтр по хосту
sudo tcpdump -i eth0 host 192.168.10.50 and port 3389
```

Windows — `pktmon` (встроен в Windows 10/Server 2019+) или Wireshark:

```cmd
pktmon start --capture --pkt-size 128 --file-name C:\temp\capture.etl
pktmon stop
pktmon etl2pcap C:\temp\capture.etl
```
