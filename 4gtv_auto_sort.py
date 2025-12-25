import requests

SOURCE_URL = "https://jody.im5k.fun/4gtv.m3u"
OUTPUT_FILE = "4gtv_sorted.m3u"

# =========================
# 分類關鍵字（可自行調整）
# =========================
NEWS = [
    "新聞", "TVBS", "鏡電視", "年代", "東森新聞", "民視新聞"
]

FINANCE = [
    "財經", "iNEWS", "SBN"
]

GENERAL = [
    "民視", "中視", "華視", "公視", "大愛", "三立", "八大", "緯來"
]

# =========================

def download_m3u(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text.splitlines()

def parse_channels(lines):
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i]
            url = lines[i + 1] if i + 1 < len(lines) else ""
            channels.append((info, url))
            i += 2
        else:
            i += 1
    return channels

def classify(info):
    for k in NEWS:
        if k in info:
            return "news"
    for k in FINANCE:
        if k in info:
            return "finance"
    for k in GENERAL:
        if k in info:
            return "general"
    return "other"

def sort_channels(channels):
    buckets = {
        "news": [],
        "finance": [],
        "general": [],
        "other": []
    }

    for ch in channels:
        category = classify(ch[0])
        buckets[category].append(ch)

    return (
        buckets["news"]
        + buckets["finance"]
        + buckets["general"]
        + buckets["other"]
    )

def save_m3u(channels, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in channels:
            f.write(info + "\n")
            f.write(url + "\n")

def run():
    try:
        print("Downloading m3u...")
        lines = download_m3u(SOURCE_URL)

        print("Parsing channels...")
        channels = parse_channels(lines)

        print("Sorting channels...")
        sorted_channels = sort_channels(channels)

        print("Saving:", OUTPUT_FILE)
        save_m3u(sorted_channels, OUTPUT_FILE)

        print("Done!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    run()
