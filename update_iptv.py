import requests

SOURCE_URL = "https://jody.im5k.fun/4gtv.m3u"
RAW_FILE = "4gtv.m3u"
SORTED_FILE = "4gtv_sorted.m3u"

# =========================
# 分類關鍵字設定
# =========================
NEWS = [
    "新聞", "TVBS", "鏡電視", "年代"
]

FINANCE = [
    "財經", "iNEWS", "SBN"
]

GENERAL = [
    "民視", "中視", "華視", "公視", "大愛", "三立"
]

# =========================

def download_m3u():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    with open(RAW_FILE, "w", encoding="utf-8") as f:
        f.write(r.text)
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

def match(info, keywords):
    return any(k in info for k in keywords)

def sort_channels(channels):
    news, finance, general, other = [], [], [], []

    for ch in channels:
        info = ch[0]
        if match(info, NEWS):
            news.append(ch)
        elif match(info, FINANCE):
            finance.append(ch)
        elif match(info, GENERAL):
            general.append(ch)
        else:
            other.append(ch)

    return news + finance + general + other

def save_m3u(channels):
    with open(SORTED_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in channels:
            f.write(info + "\n")
            f.write(url + "\n")

def run():
    try:
        # 1️⃣ 下載最新 m3u（你原本的功能）
        lines = download_m3u()

        # 2️⃣ 解析頻道
        channels = parse_channels(lines)

        # 3️⃣ 依分類排序
        sorted_channels = sort_channels(channels)

        # 4️⃣ 輸出新檔
        save_m3u(sorted_channels)

    except Exception as e:
        print("Update failed:", e)

if __name__ == "__main__":
    run()
