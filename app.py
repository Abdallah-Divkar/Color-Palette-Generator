from flask import Flask, render_template, request, jsonify
import colorsys
import random
import math

app = Flask(__name__)


# ─── Color Utilities ──────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return round(r * 255), round(g * 255), round(b * 255)


def color_name_approx(r: int, g: int, b: int) -> str:
    """Return a rough human-readable color label."""
    h, s, l = rgb_to_hsl(r, g, b)
    if l < 10:
        return "Black"
    if l > 90:
        return "White"
    if s < 12:
        return "Gray"
    hue_names = [
        (15,  "Red"), (45,  "Orange"), (70,  "Yellow"),
        (150, "Green"), (195, "Cyan"), (255, "Blue"),
        (285, "Violet"), (330, "Magenta"), (360, "Red"),
    ]
    for threshold, name in hue_names:
        if h <= threshold:
            prefix = "Light " if l > 65 else ("Dark " if l < 35 else "")
            return prefix + name
    return "Color"


def build_swatch(r: int, g: int, b: int) -> dict:
    h, s, l = rgb_to_hsl(r, g, b)
    return {
        "hex": rgb_to_hex(r, g, b),
        "rgb": {"r": r, "g": g, "b": b},
        "hsl": {"h": h, "s": s, "l": l},
        "name": color_name_approx(r, g, b),
    }


# ─── Palette Generators ───────────────────────────────────────────────────────

def generate_complementary(base_hex: str, count: int = 5) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    hues = [h, (h + 180) % 360]
    swatches = []
    step = 20
    for i, hue in enumerate(hues):
        for offset in range(-(count // 4), count // 4 + 1):
            new_l = max(20, min(80, l + offset * step))
            rgb = hsl_to_rgb(hue, s, new_l)
            swatches.append(build_swatch(*rgb))
    return swatches[:count]


def generate_analogous(base_hex: str, count: int = 5) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    angles = [h + (i - count // 2) * 30 for i in range(count)]
    return [build_swatch(*hsl_to_rgb(a % 360, s, l)) for a in angles]


def generate_triadic(base_hex: str, count: int = 6) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    hues = [(h + i * 120) % 360 for i in range(3)]
    swatches = []
    for hue in hues:
        for delta_l in [l - 15, l, l + 15]:
            swatches.append(build_swatch(*hsl_to_rgb(hue, s, max(15, min(85, delta_l)))))
    return swatches[:count]


def generate_split_complementary(base_hex: str, count: int = 5) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    hues = [h, (h + 150) % 360, (h + 210) % 360]
    swatches = [build_swatch(*hsl_to_rgb(hue, s, l)) for hue in hues]
    # pad with lightness variants
    for delta in [-20, 20]:
        swatches.append(build_swatch(*hsl_to_rgb(h, s, max(15, min(85, l + delta)))))
    return swatches[:count]


def generate_tetradic(base_hex: str, count: int = 6) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    hues = [(h + i * 90) % 360 for i in range(4)]
    swatches = [build_swatch(*hsl_to_rgb(hue, s, l)) for hue in hues]
    for delta in [-15, 15]:
        swatches.append(build_swatch(*hsl_to_rgb(h, s, max(15, min(85, l + delta)))))
    return swatches[:count]


def generate_monochromatic(base_hex: str, count: int = 6) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    steps = [15 + i * (70 / (count - 1)) for i in range(count)]
    return [build_swatch(*hsl_to_rgb(h, s, round(step, 1))) for step in steps]


def generate_shades(base_hex: str, count: int = 6) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, s, _ = rgb_to_hsl(r, g, b)
    lightnesses = [90 - i * (75 / (count - 1)) for i in range(count)]
    return [build_swatch(*hsl_to_rgb(h, s, round(lv, 1))) for lv in lightnesses]


def generate_pastel(base_hex: str, count: int = 6) -> list[dict]:
    r, g, b = hex_to_rgb(base_hex)
    h, _, _ = rgb_to_hsl(r, g, b)
    swatches = []
    for i in range(count):
        hue = (h + i * (360 / count)) % 360
        swatches.append(build_swatch(*hsl_to_rgb(hue, 45, 80)))
    return swatches


def generate_random(count: int = 6) -> list[dict]:
    h = random.uniform(0, 360)
    s = random.uniform(40, 80)
    l = random.uniform(40, 65)
    base_hex = rgb_to_hex(*hsl_to_rgb(h, s, l))
    strategies = [
        generate_analogous, generate_complementary, generate_triadic,
        generate_split_complementary, generate_monochromatic,
    ]
    return random.choice(strategies)(base_hex, count)


STRATEGIES = {
    "complementary":       generate_complementary,
    "analogous":           generate_analogous,
    "triadic":             generate_triadic,
    "split-complementary": generate_split_complementary,
    "tetradic":            generate_tetradic,
    "monochromatic":       generate_monochromatic,
    "shades":              generate_shades,
    "pastel":              generate_pastel,
}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    mode     = data.get("mode", "random")
    base_hex = data.get("color", "#3b82f6").strip()
    count    = max(3, min(12, int(data.get("count", 6))))

    if not base_hex.startswith("#") or len(base_hex) not in (4, 7):
        return jsonify({"error": "Invalid hex color"}), 400

    if mode == "random":
        palette = generate_random(count)
    elif mode in STRATEGIES:
        palette = STRATEGIES[mode](base_hex, count)
    else:
        return jsonify({"error": f"Unknown mode: {mode}"}), 400

    return jsonify({"palette": palette, "mode": mode, "base": base_hex})


@app.route("/api/modes")
def modes():
    return jsonify({"modes": list(STRATEGIES.keys()) + ["random"]})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
