"""Сравнивает два варианта знака и сохраняет лучший в docs/assets."""

from PIL import Image, ImageDraw, ImageFont

src = Image.open("assets-src/shapka.png").convert("RGBA")
box = (95, 225, 645, 645)
crop = src.crop(box)
NAVY = (13, 23, 38, 255)
SIZE = 512


def rmask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=r, fill=255)
    return m


def variant_plain(size=SIZE):
    art = crop.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(art, (0, 0), rmask((size, size), int(size * 0.22)))
    return out


def variant_tile(size=SIZE):
    tile = Image.new("RGBA", (size, size), NAVY)
    inner = crop.resize((int(size * 0.90), int(size * 0.90)), Image.LANCZOS)
    art = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    art.paste(inner, (int(size * 0.05), int(size * 0.05)))
    tile.paste(art, (0, 0), rmask((size, size), int(size * 0.18)))
    tile.putalpha(rmask((size, size), int(size * 0.22)))
    return tile


v_plain = variant_plain()
v_tile = variant_tile()

W, H = 700, 220
sheet = Image.new("RGB", (W, H), (255, 255, 255))
sheet.paste(Image.new("RGB", (W, H // 2), (32, 40, 56)), (0, H // 2))
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
except OSError:
    font = ImageFont.load_default()

for i, top in enumerate((0, H // 2)):
    for j, v in enumerate((v_plain, v_tile)):
        x = 20 + j * 320
        small = v.resize((38, 38), Image.LANCZOS)
        big = v.resize((76, 76), Image.LANCZOS)
        sheet.paste(small, (x, top + 26), small)
        sheet.paste(big, (x + 48, top + 7), big)
    color = (30, 30, 30) if i == 0 else (240, 240, 240)
    ImageDraw.Draw(sheet).text((20 + 2 * 320, top + 36), "варианты 1 и 2", font=font, fill=color)

sheet.save("assets-src/preview-book.png")
v_plain.save("assets-src/variant-plain.png")
v_tile.save("assets-src/variant-tile.png")
print("готово")
