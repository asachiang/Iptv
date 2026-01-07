import requests

SOURCE_URL = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
OUTPUT_FILE = "4gtv.m3u"

# 分類與關鍵字（順序 = 播放順序）
CATEGORY_RULES = [
    ("Litv立視", ["LiTV", "立視"]),
    ("亞太GT", ["亞太", "GT"]),
    ("體育兢技", ["體育", "運動", "兢技"]),
    ("兒童卡通", ["兒童", "卡通", "動漫", "少兒"]),
]

def fetch_m3u(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text.splitlines()

def run():
    lines = fetch_m3u(SOURCE_URL)

    categories = {name: [] for name, _ in CATEGORY_RULES}

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF") and i + 1 < len(lines):
            url = lines[i + 1].strip()

            for cat_name, keywords in CATEGORY_RULES:
                if any(k in line for k in keywords):
                    categories[cat_name].append(f"{line}\n{url}")
                    break
            i += 2
        else:
            i += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat_name, _ in CATEGORY_RULES:
            if categories[cat_name]:
                f.write("\n".join(categories[cat_name]) + "\n")

    print("✅ 已完成，只保留 4 條分類並重排完成")

if __name__ == "__main__":
    run()