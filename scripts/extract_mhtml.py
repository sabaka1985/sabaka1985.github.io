"""Извлекает текст статьи из .mhtml (Selectel) в аккуратный markdown-подобный вид."""

import email
import re
import sys
from email import policy
from pathlib import Path

from lxml import html as LH

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

raw = SRC.read_bytes()
msg = email.message_from_bytes(raw, policy=policy.default)

parts = []
for part in msg.walk():
    ctype = part.get_content_type()
    if ctype.startswith("text/"):
        payload = part.get_payload(decode=True) or b""
        parts.append((ctype, payload, part.get_content_charset() or "utf-8"))

html_bytes = b""
for ctype, payload, charset in parts:
    if ctype == "text/html" and len(payload) > len(html_bytes):
        html_bytes = payload
        used = charset

if not html_bytes:
    print("HTML не найден, части:", [(c, len(p)) for c, p, _ in parts])
    sys.exit(1)

doc = LH.fromstring(html_bytes)
for bad in doc.xpath("//script|//style|//noscript|//svg"):
    bad.getparent().remove(bad)

body = doc.body if doc.body is not None else doc

lines: list[str] = []


def text_of(el) -> str:
    return re.sub(r"\s+", " ", el.text_content()).strip()


def walk(el, depth: int = 0) -> None:
    tag = el.tag if isinstance(el.tag, str) else ""
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        t = text_of(el)
        if t:
            lines.append("")
            lines.append("#" * level + " " + t)
            lines.append("")
        return
    if tag == "p":
        t = text_of(el)
        if t:
            lines.append(t)
            lines.append("")
        return
    if tag == "pre":
        code = el.text_content().rstrip()
        if code.strip():
            lines.append("```")
            lines.append(code)
            lines.append("```")
            lines.append("")
        return
    if tag == "li":
        t = text_of(el)
        if t:
            lines.append("- " + t)
        return
    if tag == "table":
        for tr in el.xpath(".//tr"):
            cells = [text_of(td) for td in tr.xpath("./td|./th")]
            if any(cells):
                lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
        return
    if tag == "img":
        alt = el.get("alt") or ""
        src = el.get("src") or ""
        if alt.strip():
            lines.append(f"![{alt.strip()}]")
        return
    for child in el:
        walk(child, depth + 1)


walk(body)

text = "\n".join(lines)
text = re.sub(r"\n{3,}", "\n\n", text)
OUT.write_text(text, encoding="utf-8")
print(f"части: {[(c, len(p)) for c, p, _ in parts]}")
print(f"символов: {len(text)}, строк: {text.count(chr(10)) + 1}")
