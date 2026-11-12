#!/usr/bin/env python3
"""Проверка базы знаний без установки MkDocs.

Скрипт делает три вещи:
  1. проверяет, что все файлы из nav в mkdocs.yml существуют;
  2. проверяет, что все относительные ссылки в документах ведут на существующие файлы;
  3. проверяет, что на каждой странице ровно один заголовок первого уровня (#).

Запуск из корня проекта:  python scripts/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONFIG = ROOT / "mkdocs.yml"

LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
NAV_RE = re.compile(r"^\s*(?:-\s+[^:\n]+:\s*)?([\w./\-]+\.md)\s*$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)
FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


def strip_code(text: str) -> str:
    """Убирает блоки кода, чтобы комментарии `# ...` не считались заголовками."""
    return FENCE_RE.sub("", text)


def check_nav(errors: list[str]) -> int:
    text = CONFIG.read_text(encoding="utf-8")
    nav_block = text.split("\nnav:", 1)[-1]
    pages: list[str] = []
    for line in nav_block.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        item = line[2:].strip()
        path = item.rsplit(":", 1)[-1].strip() if ":" in item else item
        if path.endswith(".md"):
            pages.append(path)
    for page in pages:
        if not (DOCS / page).is_file():
            errors.append(f"nav: файл не найден — docs/{page}")
    return len(pages)


def check_links(errors: list[str]) -> int:
    checked = 0
    for md in sorted(DOCS.rglob("*.md")):
        text = strip_code(md.read_text(encoding="utf-8"))
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if not path:
                continue
            checked += 1
            resolved = (md.parent / path).resolve()
            if not resolved.exists():
                rel = md.relative_to(ROOT).as_posix()
                errors.append(f"ссылка: {rel} → {target}")
    return checked


def check_h1(errors: list[str]) -> int:
    count = 0
    for md in sorted(DOCS.rglob("*.md")):
        text = strip_code(md.read_text(encoding="utf-8"))
        headers = H1_RE.findall(text)
        count += 1
        if len(headers) != 1:
            rel = md.relative_to(ROOT).as_posix()
            errors.append(f"заголовок: {rel} — H1 найден {len(headers)} раз(а), нужен ровно один")
    return count


def main() -> int:
    errors: list[str] = []

    if not CONFIG.is_file():
        print("Не найден mkdocs.yml — запускайте скрипт из корня проекта")
        return 1

    pages = check_nav(errors)
    links = check_links(errors)
    files = check_h1(errors)

    print(f"Страниц в docs/: {files}")
    print(f"Страниц в nav:   {pages}")
    print(f"Проверено ссылок: {links}")

    if errors:
        print(f"\nПроблемы ({len(errors)}):")
        for e in errors:
            print("  -", e)
        return 1

    print("\nВсё в порядке.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
