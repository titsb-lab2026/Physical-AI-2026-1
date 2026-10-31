from PIL import Image, ImageDraw
from pathlib import Path
import random

WIDTH = 240
HEIGHT = 180

def make_pack(kind, seed=0):
    r = random.Random(seed)

    # 模擬的な撮影画像の背景
    img = Image.new("RGB", (WIDTH, HEIGHT), (230, 234, 238))
    d = ImageDraw.Draw(img)

    # パックの位置に小さなばらつきを与える
    cx = 120 + r.randint(-5, 5)
    cy = 90 + r.randint(-5, 5)

    if kind == "A":
        w, h = 112, 92
    elif kind == "B":
        w, h = 164, 62
    elif kind == "C":
        w, h = 126, 90
    else:
        raise ValueError("Unknown pack type")

    w += r.randint(-3, 3)
    h += r.randint(-3, 3)

    x0 = cx - w // 2
    y0 = cy - h // 2
    x1 = x0 + w
    y1 = y0 + h

    metal = r.randint(120, 150)
    fill = (metal, metal + 9, metal + 16)

    if kind in ("A", "B"):
        d.rounded_rectangle(
            (x0+4, y0+5, x1+4, y1+5),
            radius=9, fill=(180, 185, 190)
        )
        d.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=9, fill=fill,
            outline=(65, 78, 87), width=3
        )
        d.rounded_rectangle(
            (x0+9, y0+9, x1-9, y1-9),
            radius=4, outline=(195, 205, 212), width=2
        )

    else:
        # C型は角が欠けた異形パック
        points = [
            (x0, y0), (x1-30, y0),
            (x1, y0+30), (x1, y1),
            (x0, y1)
        ]
        d.polygon(points, fill=fill)
        d.line(points + [points[0]],
               fill=(65, 78, 87), width=3)

    # 型式ごとに異なる締結部配置
    if kind == "A":
        bolts = [
            (x0+19, y0+19),
            (x1-19, y0+19),
            (x0+19, y1-19),
            (x1-19, y1-19)
        ]

    elif kind == "B":
        bolts = [
            (x0+22, y0+19),
            (cx, y0+19),
            (x1-22, y0+19)
        ]

    else:
        bolts = [
            (x0+23, y0+24),
            (x1-25, y1-22)
        ]

    for x, y in bolts:
        d.ellipse(
            (x-7, y-7, x+7, y+7),
            fill=(214, 174, 84),
            outline=(95, 75, 42),
            width=2
        )
        d.line(
            (x-4, y, x+4, y),
            fill=(75, 60, 42),
            width=2
        )

    return img

if __name__ == "__main__":
    Path("images").mkdir(exist_ok=True)

    for kind in ("A", "B", "C"):
        filename = f"images/pack_{kind}.png"
        make_pack(kind, seed=42).save(filename)
        print("作成:", filename)

    print("3種類の模擬LiBパック画像を生成しました")
