# icon.png / icon-512.png を標準ライブラリのみで生成（電車の正面デザイン）
#   icon.png     … 180x180（apple-touch-icon 用）
#   icon-512.png … 512x512（manifest.json 用。Androidのインストール要件が192px以上のため）
# 図形の座標は 180px 基準の比率で持ち、SIZE に応じて拡大縮小する
import struct, zlib, os

BG = (26, 58, 92)          # 紺
BODY = (255, 255, 255)     # 車体（白）
WINDOW = (26, 58, 92)      # 窓（背景と同じ紺）
HEADLIGHT = (255, 193, 69) # ヘッドライト（黄）
STRIPE = (255, 193, 69)    # 前面帯（黄）

BASE = 180.0

# 車体（角丸長方形を単純な矩形として近似）
BODY_X0, BODY_Y0, BODY_X1, BODY_Y1 = 34 / BASE, 30 / BASE, 146 / BASE, 140 / BASE
# 屋根の丸み用に上部だけ少し狭める
ROOF_Y = 46 / BASE
ROOF_X0, ROOF_X1 = 44 / BASE, 136 / BASE
# 前面帯（下部）
STRIPE_Y0, STRIPE_Y1 = 116 / BASE, 128 / BASE
# 窓2つ
WIN_Y0, WIN_Y1 = 54 / BASE, 88 / BASE
WIN1_X0, WIN1_X1 = 48 / BASE, 82 / BASE
WIN2_X0, WIN2_X1 = 98 / BASE, 132 / BASE
# ヘッドライト2つ
LIGHT_Y = 128 / BASE
LIGHT_R = 7 / BASE
LIGHT1_X = 54 / BASE
LIGHT2_X = 126 / BASE

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def render(size):
    def sc(v):
        return v * size

    rows = []
    for y in range(size):
        row = bytearray([0])  # filter type 0
        py = y + 0.5
        for x in range(size):
            px = x + 0.5
            c = BG
            in_roof = py < sc(ROOF_Y)
            body_x0 = sc(ROOF_X0) if in_roof else sc(BODY_X0)
            body_x1 = sc(ROOF_X1) if in_roof else sc(BODY_X1)
            if sc(BODY_Y0) <= py < sc(BODY_Y1) and body_x0 <= px < body_x1:
                c = BODY
                if sc(WIN_Y0) <= py < sc(WIN_Y1) and (
                    sc(WIN1_X0) <= px < sc(WIN1_X1) or sc(WIN2_X0) <= px < sc(WIN2_X1)
                ):
                    c = WINDOW
                if sc(STRIPE_Y0) <= py < sc(STRIPE_Y1):
                    c = STRIPE
                for lx in (sc(LIGHT1_X), sc(LIGHT2_X)):
                    if (px - lx) ** 2 + (py - sc(LIGHT_Y)) ** 2 < sc(LIGHT_R) ** 2:
                        c = HEADLIGHT
            row += bytes(c) + b"\xff"
        rows.append(bytes(row))
    return b"".join(rows)


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))


def write_png(path, size):
    raw = render(size)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote", path, size, "x", size, len(png), "bytes")


if __name__ == "__main__":
    write_png(os.path.join(OUT_DIR, "icon.png"), 180)
    write_png(os.path.join(OUT_DIR, "icon-512.png"), 512)
