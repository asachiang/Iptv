import requests

SOURCE_URL = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
OUTPUT_FILE = "4gtv.m3u"

# 播放表列順序（只保留這四類）
ORDER = [
    "Litv立視",
    "亞太GT",
    "體育兢技",
    "兒童卡通"
]

def fetch_m3u(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text.splitlines()

def run():
    lines = fetch_m3u(SOURCE_URL)

    groups = {k: [] for k in ORDER}

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            url = lines[i + 1].strip()
            for key in ORDER:
                if key in line:
                    groups[key].append(f"{line}\n{url}")
                    break
            i += 2
        else:
            i += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for key in ORDER:
            if groups[key]:
                f.write("\n".join(groups[key]) + "\n")

    print("✅ 已完成：只保留並排序指定四個分類 → 4gtv.m3u")

if __name__ == "__main__":
    run()