"""Збирає гру: tea_database.csv -> teas.js, texts.csv -> texts.js, іконки, автономний HTML.
Запуск:  python3 build.py [шлях_до_csv]
"""
import csv, json, re, sys, pathlib
root = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else root / "tea_database.csv"

def weight(w):
    m = re.fullmatch(r'\s*1\s*г?\s*[\\/]\s*(\d+)\s*(?:мл)?\s*', w)
    return f"1г / {m.group(1)}мл" if m else w.strip()

def temp(t):
    t = t.strip().replace("-", "–")
    return t + "°C" if re.fullmatch(r'[\d–\s]+', t) else t

def split(s):
    return [x.strip() for x in s.split(";") if x.strip()]

teas = []
with open(src, encoding="utf-8-sig", newline="") as f:
    for i, r in enumerate(csv.DictReader(f), 1):
        if r["В меню"].strip().lower() != "так":
            continue
        teas.append({
            "id": f"t{i}", "name": r["Назва"].strip(), "type": r["Тип чаю"].strip(),
            "region": r["Регіон"].strip(), "novice": r["Для новачків"].strip() == "так",
            "char": r["Характер"].strip(), "art": r["Артикул"].strip(),
            "desc": split(r["Дескриптори"]), "time": r["Час доби"].strip() or "Будь-який",
            "vessels": split(r["Посуд"]), "weight": weight(r["Вага"]), "temp": temp(r["Температура"]),
            "infusions": r["Проливи"].strip(), "pour": r["Злив"].strip(),
            "comment": r["Коментар"].strip(), "about": r["Про чай"].strip(),
        })
js = "const TEAS=" + json.dumps(teas, ensure_ascii=False, indent=0) + ";\n"
(root / "teas.js").write_text(js, encoding="utf-8")

# тексти інтерфейсу: texts.csv -> texts.js
tx = {}
with open(root / "texts.csv", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        if r["key"].strip():
            tx[r["key"].strip()] = r["text"]
js_tx = "const TX=" + json.dumps(tx, ensure_ascii=False, indent=0) + ";\n"
(root / "texts.js").write_text(js_tx, encoding="utf-8")

# автономна версія: усе в одному файлі
html = (root / "index.html").read_text(encoding="utf-8")
html = html.replace('<script src="teas.js"></script>', "<script>\n" + js + "</script>")
html = html.replace('<script src="texts.js"></script>', "<script>\n" + js_tx + "</script>")
html = re.sub(r'<link rel="manifest"[^>]*>\n?', "", html)
html = re.sub(r'<link rel="icon"[^>]*>\n?', "", html)
(root / "chaina-zala-standalone.html").write_text(html, encoding="utf-8")

# іконки
from PIL import Image, ImageDraw
for size in (192, 512):
    im = Image.new("RGB", (size, size), "#0f2529")
    d = ImageDraw.Draw(im); c = size / 2
    def circ(r, fill=None, outline=None, w=0):
        d.ellipse([c - r, c - r, c + r, c + r], fill=fill, outline=outline, width=w)
    circ(size * .31, outline="#a9d6c0", w=max(3, size // 32))
    circ(size * .235, fill="#c98544")
    circ(size * .12, fill="#e0a45f")
    s = size * .15
    d.rounded_rectangle([size * .60, size * .60, size * .60 + s, size * .60 + s], radius=size * .03, fill="#b3283c")
    im.save(root / f"icon-{size}.png")
print(len(teas), "чаїв ->", "teas.js, chaina-zala-standalone.html, icon-192.png, icon-512.png")
