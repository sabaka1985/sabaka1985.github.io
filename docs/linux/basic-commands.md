---
tags:
  - linux
  - команды
---

# Базовые команды Linux

## Файлы и каталоги

```bash
pwd                       # где я
ls -lah                   # список с правами и размерами
cd /var/log               # перейти
cp -r src/ dst/           # копировать рекурсивно
mv old.txt new.txt        # переименовать/переместить
rm -rf build/             # удалить (осторожно!)
mkdir -p /data/app/logs   # создать со всеми родителями
```

## Просмотр и поиск

```bash
cat file.log              # весь файл
less file.log             # постранично (q — выход, / — поиск)
tail -f /var/log/syslog   # следить в реальном времени
head -n 50 access.log     # первые 50 строк
grep -rn "error" /etc/nginx/          # рекурсивно с номерами строк
grep -i "timeout" app.log | tail -20
```

Поиск файлов:

```bash
find /var/log -name "*.log" -mtime -1          # изменённые за сутки
find / -type f -size +500M 2>/dev/null         # крупные файлы
which python3                                  # путь к исполняемому файлу
```

## Права доступа

```bash
ls -l file            # -rw-r--r-- 1 user group
chmod 644 file        # rw-r--r--
chmod 755 script.sh   # rwxr-xr-x
chmod +x script.sh    # добавить бит исполнения
chown user:group file # сменить владельца
umask                 # маска прав по умолчанию
```

Расшифровка `-rwxr-xr--`: владелец `rwx` = 7, группа `r-x` = 5, остальные `r--` = 4.

## Процессы

```bash
ps aux | grep nginx       # найти процесс
top                       # интерактивный монитор (htop удобнее)
kill -15 1234             # вежливо завершить
kill -9 1234              # убить (крайняя мера)
pgrep -a nginx            # PID по имени
lsof -i :8080             # кто занял порт
```

## Пользователи и sudo

```bash
whoami
id
sudo -i                   # стать root
useradd -m -s /bin/bash ivan
passwd ivan
usermod -aG sudo ivan     # добавить в группу sudo
```

## Сеть

```bash
ip a                      # адреса
ip r                      # маршруты
ss -tulpn                 # слушающие порты
ping -c 4 8.8.8.8
curl -I https://example.com
wget -O file.zip https://example.com/file.zip
dig example.com +short
traceroute example.com
```

## Архивы

```bash
tar -czf backup.tar.gz /data/app      # создать
tar -xzf backup.tar.gz -C /tmp        # распаковать
tar -tzf backup.tar.gz | head         # посмотреть содержимое
zip -r arch.zip dir/
unzip arch.zip -d /tmp
```

## Диски

```bash
df -h                     # занятое место по ФС
du -sh /var/log/* | sort -h      # что занимает место
lsblk                     # блочные устройства
mount /dev/sdb1 /mnt/data
```
