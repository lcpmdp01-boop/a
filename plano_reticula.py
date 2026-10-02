import math
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
except ModuleNotFoundError as exc:
    if exc.name != "matplotlib":
        raise
    plt = None


def line_segment_in_rect(line_type, value, w, h, eps=1e-9):
    """
    Devuelve los 2 puntos de intersección de la recta con el rectángulo [0,w]x[0,h].
    line_type: 'sum' para x + y = value, 'diff' para x - y = value
    """
    pts = []

    if line_type == 'sum':  # x + y = c
        c = value
        candidates = [
            (0.0, c),        # x=0
            (w, c - w),      # x=w
            (c, 0.0),        # y=0
            (c - h, h),      # y=h
        ]
    elif line_type == 'diff':  # x - y = k
        k = value
        candidates = [
            (0.0, -k),       # x=0
            (w, w - k),      # x=w
            (k, 0.0),        # y=0
            (h + k, h),      # y=h
        ]
    else:
        raise ValueError("line_type debe ser 'sum' o 'diff'.")

    for x, y in candidates:
        if -eps <= x <= w + eps and -eps <= y <= h + eps:
            x = min(max(x, 0.0), w)
            y = min(max(y, 0.0), h)
            if not any(abs(x - px) < eps and abs(y - py) < eps for px, py in pts):
                pts.append((x, y))

    if len(pts) < 2:
        return None
    if len(pts) > 2:
        # En casos degenerados (paso por esquina), quedarse con extremos más alejados
        max_d = -1.0
        best = None
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
                if d > max_d:
                    max_d = d
                    best = (pts[i], pts[j])
        return best
    return pts[0], pts[1]


def generate_pattern_values(min_v, max_v, base_steps):
    """Genera valores desde min_v a max_v con patrón repetido de incrementos."""
    vals = []

    v = 0.0
    while v - max_v <= 1e-9:
        if v + 1e-9 >= min_v:
            vals.append(v)
        v += base_steps[len(vals) % len(base_steps)] if vals else base_steps[0]

    v = -base_steps[0]
    idx = 1
    while v + 1e-9 >= min_v:
        if v <= max_v + 1e-9:
            vals.append(v)
        v -= base_steps[idx % len(base_steps)]
        idx += 1

    return sorted(set(round(x, 10) for x in vals if min_v - 1e-9 <= x <= max_v + 1e-9))


def export_without_matplotlib():
    """Exporta SVG y PNG de 300 dpi sin paquetes externos ni interfaz gráfica."""
    import struct
    import unicodedata
    import zlib
    from html import escape
    from pathlib import Path

    # Un mismo sistema de coordenadas para ambos formatos; origen SO.
    scale = 20
    width, height = 3600, 2600
    pixels = bytearray(b"\xff" * (width * height * 3))
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    def point(x, y):
        return round((x + 5) * scale), round((118 - y) * scale)

    def line(x1, y1, x2, y2, color="black", stroke=4):
        a, b = point(x1, y1), point(x2, y2)
        rgb = {"black": b"\x00\x00\x00", "red": b"\xff\x00\x00",
               "#FFD400": b"\xff\xd4\x00"}[color]
        svg.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" '
                   f'y2="{b[1]}" stroke="{color}" stroke-width="{stroke}"/>')
        dx, dy = b[0] - a[0], b[1] - a[1]
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = round(a[0] + dx * i / steps)
            y = round(a[1] + dy * i / steps)
            for row in range(max(0, y - stroke // 2), min(height, y + (stroke + 1) // 2)):
                left, right = max(0, x - stroke // 2), min(width, x + (stroke + 1) // 2)
                if left < right:
                    start = (row * width + left) * 3
                    pixels[start:start + (right - left) * 3] = rgb * (right - left)

    # Fuente bitmap 5x7 para que las etiquetas PNG tampoco necesiten dependencias.
    glyphs = {
        "A": "01110 10001 10001 11111 10001 10001 10001",
        "B": "11110 10001 10001 11110 10001 10001 11110",
        "C": "01111 10000 10000 10000 10000 10000 01111",
        "D": "11110 10001 10001 10001 10001 10001 11110",
        "E": "11111 10000 10000 11110 10000 10000 11111",
        "F": "11111 10000 10000 11110 10000 10000 10000",
        "G": "01111 10000 10000 10111 10001 10001 01111",
        "H": "10001 10001 10001 11111 10001 10001 10001",
        "I": "11111 00100 00100 00100 00100 00100 11111",
        "J": "00111 00010 00010 00010 10010 10010 01100",
        "K": "10001 10010 10100 11000 10100 10010 10001",
        "L": "10000 10000 10000 10000 10000 10000 11111",
        "M": "10001 11011 10101 10101 10001 10001 10001",
        "N": "10001 11001 10101 10011 10001 10001 10001",
        "O": "01110 10001 10001 10001 10001 10001 01110",
        "P": "11110 10001 10001 11110 10000 10000 10000",
        "Q": "01110 10001 10001 10001 10101 10010 01101",
        "R": "11110 10001 10001 11110 10100 10010 10001",
        "S": "01111 10000 10000 01110 00001 00001 11110",
        "T": "11111 00100 00100 00100 00100 00100 00100",
        "U": "10001 10001 10001 10001 10001 10001 01110",
        "V": "10001 10001 10001 10001 10001 01010 00100",
        "W": "10001 10001 10001 10101 10101 10101 01010",
        "X": "10001 10001 01010 00100 01010 10001 10001",
        "Y": "10001 10001 01010 00100 00100 00100 00100",
        "Z": "11111 00001 00010 00100 01000 10000 11111",
        "0": "01110 10001 10011 10101 11001 10001 01110",
        "1": "00100 01100 00100 00100 00100 00100 01110",
        "2": "01110 10001 00001 00010 00100 01000 11111",
        "3": "11110 00001 00001 01110 00001 00001 11110",
        "4": "00010 00110 01010 10010 11111 00010 00010",
        "5": "11111 10000 10000 11110 00001 00001 11110",
        "6": "01110 10000 10000 11110 10001 10001 01110",
        "7": "11111 00001 00010 00100 01000 01000 01000",
        "8": "01110 10001 10001 01110 10001 10001 01110",
        "9": "01110 10001 10001 01111 00001 00001 01110",
        "-": "00000 00000 00000 11111 00000 00000 00000",
        "/": "00001 00010 00010 00100 01000 01000 10000",
        ",": "00000 00000 00000 00000 00100 00100 01000",
        ":": "00000 00100 00100 00000 00100 00100 00000",
        " ": "00000 00000 00000 00000 00000 00000 00000",
    }

    def text(x, y, label, size=3):
        px, py = point(x, y)
        svg.append(f'<text x="{px}" y="{py + 7 * size}" '
                   f'font-family="monospace" font-size="{9 * size}">{escape(label)}</text>')
        label = unicodedata.normalize("NFKD", label.upper())
        label = "".join(c for c in label if not unicodedata.combining(c))
        for c in label:
            for row, bits in enumerate(glyphs[c].split()):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        for yy in range(py + row * size, py + (row + 1) * size):
                            left = px + col * size
                            if 0 <= yy < height and 0 <= left <= width - size:
                                start = (yy * width + left) * 3
                                pixels[start:start + size * 3] = b"\x00" * (size * 3)
            px += 6 * size

    for i in range(41):
        line(0, i * 2.5, 100, i * 2.5, "#FFD400", 2)
    for i in range(51):
        line(i * 2, 0, i * 2, 100, "#FFD400", 2)
    steps = [p * math.sqrt(2) for p in (4, 8, 12, 16)]
    for family, lower, upper in (("sum", 0, 200), ("diff", -100, 100)):
        for value in generate_pattern_values(lower, upper, steps):
            segment = line_segment_in_rect(family, value, 100, 100)
            if segment:
                (x1, y1), (x2, y2) = segment
                line(x1, y1, x2, y2, "red", 5)
    for coords in ((0, 0, 100, 0), (100, 0, 100, 100),
                   (100, 100, 0, 100), (0, 100, 0, 0)):
        line(*coords, stroke=5)
    line(50, 104, 50, 112)
    line(48.5, 109, 50, 112)
    line(51.5, 109, 50, 112)
    text(49.4, 116, "N", 4)
    line(108, 8, 128, 8)
    for x, label in ((108, "0"), (118, "10"), (128, "20 m")):
        line(x, 7, x, 9)
        text(x - 0.5, 5, label)
    labels = ("Amarillo:", "E-O cada 2,5 m", "N-S cada 2,0 m", "",
              "Rojo: NE-SW y NW-SE", "Separacion perpendicular",
              "Patron 4/8/12/16 m")
    for i, label in enumerate(labels):
        text(108, 95 - i * 3, label)
    svg.append("</svg>")
    Path("plano_reticula.svg").write_text("\n".join(svg), encoding="utf-8")

    def chunk(kind, data):
        return (struct.pack("!I", len(data)) + kind + data
                + struct.pack("!I", zlib.crc32(kind + data) & 0xffffffff))

    raw = bytearray()
    for row in range(height):
        raw.append(0)  # PNG: sin filtro.
        raw.extend(pixels[row * width * 3:(row + 1) * width * 3])
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
           + chunk(b"pHYs", struct.pack("!2IB", 11811, 11811, 1))
           + chunk(b"IDAT", zlib.compress(raw))
           + chunk(b"IEND", b""))
    Path("plano_reticula.png").write_bytes(png)


def main():
    if plt is None:
        export_without_matplotlib()
        return

    # Parámetros principales
    W, H = 100.0, 100.0
    grid_color = "#FFD400"

    fig, ax = plt.subplots(figsize=(12, 10), facecolor="white")
    ax.set_facecolor("white")

    # Marco negro
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, edgecolor="black", linewidth=2.2, zorder=5))

    # Retícula amarilla delgada
    y = 0.0
    while y <= H + 1e-9:
        ax.plot([0, W], [y, y], color=grid_color, linewidth=1, zorder=1)
        y += 2.5

    x = 0.0
    while x <= W + 1e-9:
        ax.plot([x, x], [0, H], color=grid_color, linewidth=1, zorder=1)
        x += 2.0

    # Líneas rojas diagonales con separación perpendicular variable 4/8/12/16 m
    pattern = [4.0, 8.0, 12.0, 16.0]
    dk = [p * math.sqrt(2) for p in pattern]  # incrementos para c y k

    # Familia 1: x + y = c, rango útil [0, W+H]
    c_vals = []
    c = 0.0
    i = 0
    while c <= W + H + 1e-9:
        c_vals.append(c)
        c += dk[i % len(dk)]
        i += 1
    c = -dk[0]
    i = 1
    while c >= -1e-9:
        c_vals.append(c)
        c -= dk[i % len(dk)]
        i += 1

    for c in sorted(set(round(v, 10) for v in c_vals if -1e-9 <= v <= W + H + 1e-9)):
        seg = line_segment_in_rect('sum', c, W, H)
        if seg:
            (x1, y1), (x2, y2) = seg
            ax.plot([x1, x2], [y1, y2], color="red", linewidth=2.2, zorder=3)

    # Familia 2: x - y = k, rango útil [-H, W]
    k_vals = [0.0]
    k = 0.0
    i = 0
    while True:
        k += dk[i % len(dk)]
        i += 1
        if k > W + 1e-9:
            break
        k_vals.append(k)
    k = 0.0
    i = 0
    while True:
        k -= dk[i % len(dk)]
        i += 1
        if k < -H - 1e-9:
            break
        k_vals.append(k)

    for k in sorted(set(round(v, 10) for v in k_vals if -H - 1e-9 <= v <= W + 1e-9)):
        seg = line_segment_in_rect('diff', k, W, H)
        if seg:
            (x1, y1), (x2, y2) = seg
            ax.plot([x1, x2], [y1, y2], color="red", linewidth=2.2, zorder=3)

    # Flecha de Norte y letra N (fuera del marco)
    nx = W * 0.5
    ax.annotate(
        "",
        xy=(nx, H + 12),
        xytext=(nx, H + 4),
        arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.8),
        annotation_clip=False,
        zorder=10,
    )
    ax.text(nx, H + 13.5, "N", ha="center", va="bottom", fontsize=13, fontweight="bold")

    # Barra de escala 0-10-20 m (fuera del marco)
    sb_x0, sb_y = W + 8, 8
    ax.plot([sb_x0, sb_x0 + 20], [sb_y, sb_y], color="black", linewidth=2)
    ax.plot([sb_x0, sb_x0], [sb_y - 1, sb_y + 1], color="black", linewidth=2)
    ax.plot([sb_x0 + 10, sb_x0 + 10], [sb_y - 1, sb_y + 1], color="black", linewidth=2)
    ax.plot([sb_x0 + 20, sb_x0 + 20], [sb_y - 1, sb_y + 1], color="black", linewidth=2)
    ax.text(sb_x0, sb_y - 3, "0", ha="center", va="top", fontsize=9)
    ax.text(sb_x0 + 10, sb_y - 3, "10", ha="center", va="top", fontsize=9)
    ax.text(sb_x0 + 20, sb_y - 3, "20 m", ha="center", va="top", fontsize=9)

    # Leyenda fuera del marco
    legend_x = W + 8
    legend_y = H - 5
    ax.text(
        legend_x,
        legend_y,
        "Amarillo: E–O cada 2,5 m; N–S cada 2,0 m\n"
        "Rojo: NE–SW y NW–SE; separación perpendicular 4–16 m (patrón 4/8/12/16)",
        ha="left",
        va="top",
        fontsize=9.5,
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.35"),
    )

    # Estilo general
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.set_xlim(-5, W + 55)
    ax.set_ylim(-8, H + 18)

    # Exportaciones
    fig.savefig("plano_reticula.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig("plano_reticula.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
