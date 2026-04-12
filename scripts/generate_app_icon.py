from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SPRITE_SHEET = ASSETS / "cats_raccoons_walk_attack_pretty.png"
PNG_OUT = ASSETS / "app_icon.png"
ICO_OUT = ASSETS / "app_icon.ico"

CELL_W = 96
CELL_H = 96
ICON_SIZE = 1024


def crop_frame(image, col, row):
    box = (
        col * CELL_W,
        row * CELL_H,
        (col + 1) * CELL_W,
        (row + 1) * CELL_H,
    )
    frame = image.crop(box)
    alpha_box = frame.getchannel("A").getbbox()
    if alpha_box:
        frame = frame.crop(alpha_box)
    return frame


def make_radial_glow(size, inner_color, outer_color):
    glow = Image.new("RGBA", (size, size), outer_color)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    margin = size // 14
    draw.ellipse((margin, margin, size - margin, size - margin), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(size // 10))
    inner = Image.new("RGBA", (size, size), inner_color)
    return Image.composite(inner, glow, mask)


def make_background():
    base = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (20, 24, 31, 255))
    draw = ImageDraw.Draw(base)

    draw.rounded_rectangle(
        (36, 36, ICON_SIZE - 36, ICON_SIZE - 36),
        radius=220,
        fill=(43, 50, 61, 255),
    )

    left_glow = make_radial_glow(ICON_SIZE, (255, 181, 65, 255), (43, 50, 61, 0))
    right_glow = make_radial_glow(ICON_SIZE, (145, 151, 163, 255), (43, 50, 61, 0))
    base.alpha_composite(left_glow, (-170, -40))
    base.alpha_composite(right_glow, (170, 60))

    draw.pieslice((70, 80, 954, 964), start=120, end=300, fill=(255, 170, 48, 220))
    draw.pieslice((70, 80, 954, 964), start=300, end=120, fill=(149, 156, 166, 215))
    draw.ellipse((118, 128, 906, 916), outline=(248, 231, 198, 255), width=24)
    draw.ellipse((166, 176, 858, 868), outline=(28, 30, 36, 120), width=10)

    for y in (250, 780):
        draw.rounded_rectangle((240, y, 784, y + 18), radius=9, fill=(248, 231, 198, 95))

    return base


def add_shadow(canvas, sprite, center, scale, blur_radius=26, alpha=100):
    shadow = sprite.resize(scale, Image.Resampling.NEAREST)
    shadow = Image.new("RGBA", shadow.size, (0, 0, 0, alpha)).convert("RGBA")
    sprite_alpha = sprite.resize(scale, Image.Resampling.NEAREST).getchannel("A")
    shadow.putalpha(sprite_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    x = center[0] - shadow.width // 2
    y = center[1] - shadow.height // 2 + 18
    canvas.alpha_composite(shadow, (x, y))


def paste_sprite(canvas, sprite, center, scale, rotation):
    scaled = sprite.resize(scale, Image.Resampling.NEAREST)
    rotated = scaled.rotate(rotation, resample=Image.Resampling.NEAREST, expand=True)
    x = center[0] - rotated.width // 2
    y = center[1] - rotated.height // 2
    canvas.alpha_composite(rotated, (x, y))


def add_scratches(canvas):
    scratch = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scratch)
    lines = [
        ((332, 184), (412, 314)),
        ((376, 160), (458, 294)),
        ((420, 138), (503, 276)),
        ((590, 708), (674, 852)),
        ((634, 682), (720, 826)),
        ((678, 660), (764, 804)),
    ]
    for start, end in lines:
        draw.line([start, end], fill=(248, 231, 198, 120), width=12)
        draw.line(
            [(start[0] + 12, start[1] - 8), (end[0] + 12, end[1] - 8)],
            fill=(28, 30, 36, 70),
            width=4,
        )
    scratch = scratch.filter(ImageFilter.GaussianBlur(1))
    canvas.alpha_composite(scratch)


def main():
    sheet = Image.open(SPRITE_SHEET).convert("RGBA")
    cat = crop_frame(sheet, 2, 1)
    raccoon = crop_frame(sheet, 2, 4)

    icon = make_background()

    add_shadow(icon, cat, (362, 548), (350, 350))
    add_shadow(icon, raccoon, (670, 546), (350, 350))
    paste_sprite(icon, cat, (356, 524), (350, 350), -8)
    paste_sprite(icon, raccoon, (676, 520), (350, 350), 8)
    add_scratches(icon)

    # Add contrast and a soft vignette so the icon reads at small sizes.
    vignette = Image.new("L", (ICON_SIZE, ICON_SIZE), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse((56, 56, ICON_SIZE - 56, ICON_SIZE - 56), fill=210)
    vignette = ImageChops.invert(vignette.filter(ImageFilter.GaussianBlur(90)))
    vignette_layer = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    vignette_layer.putalpha(vignette)
    icon.alpha_composite(vignette_layer)

    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)
    icon.save(PNG_OUT)
    icon.save(ICO_OUT, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Saved {PNG_OUT}")
    print(f"Saved {ICO_OUT}")


if __name__ == "__main__":
    main()
