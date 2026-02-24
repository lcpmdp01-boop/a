import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


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


def main():
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
