# IT База знаний

Личная база знаний на **MkDocs + Material for MkDocs**, публикуется как сайт через **GitHub Pages**.

Разделы: Сети · Windows Server · 1С · Linux · Базы данных · PowerShell · Cisco · Траблшутинг.

---

## Быстрый старт (локально)

```bash
cd it-kb

# 1. виртуальное окружение
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. зависимости
pip install -r requirements.txt

# 3. предпросмотр на http://127.0.0.1:8000
mkdocs serve
```

Сайт пересобирается автоматически при сохранении любого файла в `docs/`.

Собрать готовый сайт в папку `site/`:

```bash
mkdocs build
```

## Проверка без MkDocs

Если MkDocs ещё не установлен, структуру и ссылки можно проверить обычным Python:

```bash
python scripts/check_links.py
```

Скрипт проверяет, что все страницы из `nav` существуют, все относительные ссылки
ведут на реальные файлы и на каждой странице ровно один заголовок `#`.

## Публикация на GitHub Pages

1. Создайте на GitHub пустой репозиторий, например `it-kb` (без README).
2. Замените `USERNAME` на свой логин в `mkdocs.yml` (`site_url`, `repo_name`, `repo_url`).
3. Залейте проект (Windows, PowerShell).

   Откройте PowerShell в папке проекта — в Проводнике: `Shift` + правый клик по папке `it-kb` → **Открыть окно PowerShell здесь**.

```powershell
cd C:\Users\Pavel\Documents\deepseek-harness\default-workspace\it-kb

# 0. если Git ещё не установлен (потом перезапустить терминал):
#    winget install --id Git.Git -e --source winget

# 1. однократная настройка: кто автор коммитов
git config --global user.name "Иван Петров"
git config --global user.email "ivan@example.com"

# 2. однократная настройка Windows: UTF-8 в консоли и правильные переводы строк
git config --global core.autocrlf true
git config --global i18n.commitEncoding utf-8
chcp 65001 > $null
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8

# 3. создаём репозиторий и делаем первый коммит
git init
git add .
git commit -m "База знаний: первый коммит"
git branch -M main

# 4. связываем с GitHub и отправляем
git remote add origin https://github.com/USERNAME/it-kb.git
git push -u origin main
```

   > **Важно:** без шага 1 `git commit` упадёт с ошибкой `Author identity unknown`.
   > Проверить, задано ли имя и почта: `git config --global user.name` и `git config --global user.email`.

   Что произойдёт на шаге 4: Git спросит логин и пароль. В Git for Windows уже встроен
   **Git Credential Manager** — при первом `push` откроется окно браузера для входа в GitHub,
   и пароль вводить не нужно. Если браузерный вход не сработал — используйте **Personal Access Token**:
   GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token**,
   права — `repo` (для приватного репозитория) или `public_repo`; в качестве пароля вставьте сам токен.

   Если `git commit` ругается на кириллицу в сообщении — используйте английский текст:
   `git commit -m "Knowledge base: initial commit"`.

   <details>
   <summary>То же самое для cmd.exe</summary>

```bat
cd /d C:\Users\Pavel\Documents\deepseek-harness\default-workspace\it-kb
chcp 65001
git init
git add .
git commit -m "Knowledge base: initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/it-kb.git
git push -u origin main
```

   </details>

   <details>
   <summary>Для Linux / macOS</summary>

```bash
cd it-kb
git init
git add .
git commit -m "База знаний: первый коммит"
git branch -M main
git remote add origin https://github.com/USERNAME/it-kb.git
git push -u origin main
```

   </details>

4. В репозитории: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
5. Каждый `git push` в `main` запускает workflow `.github/workflows/deploy.yml` и обновляет сайт.

Адрес сайта: `https://USERNAME.github.io/it-kb/`

> Если репозиторий приватный, GitHub Pages на бесплатном плане недоступен — нужен Pro/Team.

### Ошибся с адресом репозитория

`error: remote origin already exists` — remote уже создан, а `git remote add` добавляет новый,
а не меняет существующий. Менять адрес нужно через `set-url`:

```powershell
git remote -v                                                    # посмотреть текущий адрес
git remote set-url origin https://github.com/ЛОГИН/it-kb.git     # заменить на свой
git remote -v                                                    # убедиться, что заменилось
```

Если нужно начать с чистого листа:

```powershell
git remote remove origin
git remote add origin https://github.com/ЛОГИН/it-kb.git
```

Проверить, что репозиторий на GitHub уже создан и доступен (не ошибка — пустой вывод,
значит репозиторий пустой и готов принять первый `push`):

```powershell
$env:GIT_TERMINAL_PROMPT = "0"
git ls-remote https://github.com/ЛОГИН/it-kb.git
```


## Аналитика посещений

Поддерживаются два счётчика, включаются в `mkdocs.yml` независимо друг от друга:

```yaml
extra:
  goatcounter: sabaka1985   # имя аккаунта, https://<код>.goatcounter.com
  metrika: ""               # номер счётчика Яндекс.Метрики
```

Пустое значение выключает счётчик — скрипт просто не попадает в страницы. Сниппеты живут
в `overrides/main.html`, который подключён через `theme.custom_dir`.

**GoatCounter** — бесплатный, без куки и баннеров. Регистрация: [goatcounter.com/signup](https://www.goatcounter.com/signup),
поле **Account name** и станет поддоменом для входа в статистику.

**Яндекс.Метрика** — если GoatCounter недоступен из вашей сети или нужны вебвизор и карты
кликов. Номер счётчика берётся в [metrika.yandex.ru](https://metrika.yandex.ru) после создания
счётчика с адресом `https://sabaka1985.github.io/it-kb/`.

Полезно знать: счётчики блокируются расширениями (20–40 % визитов теряется), локальные
просмотры `mkdocs serve` не считаются.

## Структура

```
it-kb/
├── mkdocs.yml                  # вся конфигурация: навигация, тема, плагины
├── requirements.txt            # версия mkdocs-material
├── .github/workflows/deploy.yml
├── overrides/main.html         # свой шаблон: счётчик GoatCounter
├── scripts/check_links.py      # проверка ссылок и структуры
└── docs/
    ├── index.md                # главная страница с плитками разделов
    ├── tags.md                 # автоматический список тегов
    ├── networks/               # Сети
    ├── windows-server/         # Windows Server
    ├── 1c/                     # 1С
    ├── linux/                  # Linux
    ├── databases/              # Базы данных
    ├── powershell/             # PowerShell
    ├── cisco/                  # Cisco
    └── troubleshooting/        # Траблшутинг
```

## Как добавить новую страницу

1. Создайте файл, например `docs/networks/nat.md`.
2. Добавьте его в `nav` в `mkdocs.yml`:

```yaml
  - Сети:
      - networks/index.md
      - Модель OSI и TCP/IP: networks/osi.md
      - VLAN и trunk: networks/vlan.md
      - NAT и PAT: networks/nat.md   # ← новая строка
```

3. Добавьте ссылку на страницу в `docs/networks/index.md`.

Файл без строки в `nav` тоже соберётся, но не попадёт в меню.

## Соглашения

- Один файл — одна тема, имя файла латиницей в нижнем регистре: `reset-password-ad.md`.
- В начале страницы — блок метаданных:

```markdown
---
tags:
  - windows
  - active directory
---
```

- Заголовок первого уровня (`#`) в файле один и совпадает с названием в меню.
- Ссылки между страницами — относительные: `[см. GPO](../windows-server/gpo.md)`.

## Обновление темы

```bash
pip install --upgrade mkdocs-material
pip freeze > requirements.txt
```
