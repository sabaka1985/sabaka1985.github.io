---
tags:
  - linux
  - systemd
---

# systemd

## Управление службами

```bash
systemctl status nginx
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl reload nginx          # перечитать конфиг без разрыва соединений
systemctl enable nginx          # автозапуск
systemctl disable nginx
systemctl list-units --failed
systemctl list-unit-files --state=enabled
```

## Свой юнит

Файл `/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=My Application
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/myapp
EnvironmentFile=/etc/myapp/env
ExecStart=/opt/myapp/bin/myapp --config /etc/myapp/config.yaml
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Применить:

```bash
systemctl daemon-reload
systemctl enable --now myapp
systemctl status myapp
```

Типы `Type`: `simple` (по умолчанию), `forking` (демон уходит в фон), `notify` (сообщает о готовности), `oneshot` (разовая задача).

## journalctl

```bash
journalctl -u nginx -f              # следить за службой
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx -p err          # только ошибки
journalctl -b -1                    # журнал предыдущей загрузки
journalctl --disk-usage
journalctl --vacuum-time=14d        # чистить старше 14 дней
```

## Таймеры вместо cron

`/etc/systemd/system/backup.timer`:

```ini
[Unit]
Description=Daily backup

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

В паре с `backup.service`, у которого `Type=oneshot` и `ExecStart=/usr/local/bin/backup.sh`.

```bash
systemctl enable --now backup.timer
systemctl list-timers --all
```

Плюсы таймеров: журнал, `Persistent=true` (догонит пропущенный запуск), зависимости,
защита от параллельного запуска.

## Грабли

!!! warning "Частое"
    - Забыли `daemon-reload` — systemd не видит новый юнит.
    - `Type=simple`, а процесс форкается → система считает службу упавшей.
    - Нет `Wants=network-online.target` — сервис стартует до сети и падает.
    - Рабочий каталог не задан — относительные пути ломаются.
    - Права: служба работает от `app`, а файлы принадлежат `root`.
