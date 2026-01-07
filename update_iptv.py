import requests
import os

def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text.splitlines()
    except Exception as e:
        print(f"無法抓取 {url}: {e}")
        return []

def validate_url(url):
    try:
        r = requests.get(url, timeout=3, stream=True)
        return r.status_code == 200
    except:
        return False

def run():
    # ===== 來源 =====
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    URL_TH = "https://iptv-org.github.io/iptv/countries/th.m3u"
    URL_LITV = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
    YT_FILE = "youtube 新聞.m3u"

    # ===== 分類 =====
    categories = {
        "LITV": [],
        "NEWS": [],
        "GENERAL": [],
        "KIDS": [],
        "SPORT": [],
        "MUSIC": [],
        "OTHER": [],
        "TH": [],
        "WS_V4": [],
        "YS_V4": [],
        "K48": []
    }

    # ===== Litv 立視 =====
    litv_lines = fetch_m3u(URL_LITV)
    i = 0
    while i < len(litv_lines):
        if litv_lines[i].startswith("#EXTINF"):
            categories["LITV"].append(f"{litv_lines[i]}\n{litv_lines[i+1]}")
            i += 2
        else:
            i += 1

    # ===== 4GTV =====
    lines_4gtv = fetch_m3u(URL_4GTV)
    i = 0
    while i < len(lines_4gtv):
        line = lines_4gtv[i]
        if line.startswith("#EXTINF"):
            url = lines_4gtv[i+1]
            if any(k in line for k in ["新聞", "財經"]):
                categories["NEWS"].append(f"{line}\n{url}")
            elif any(k in line for k in ["兒童", "少兒", "動漫"]):
                categories["KIDS"].append(f"{line}\n{url}")
            elif any(k in line for k in ["體育", "運動"]):
                categories["SPORT"].append(f"{line}\n{url}")
            elif any(k in line for k in ["音樂", "綜藝", "娛樂"]):
                categories["MUSIC"].append(f"{line}\n{url}")
            elif "綜合" in line:
                categories["GENERAL"].append(f"{line}\n{url}")
            else:
                categories["OTHER"].append(f"{line}\n{url}")
            i += 2
        else:
            i += 1

    # ===== Thailand（驗證）=====
    print("篩選 Thailand 頻道...")
    th_lines = fetch_m3u(URL_TH)
    valid_th = []
    for i in range(len(th_lines)):
        if th_lines[i].startswith("#EXTINF"):
            url = th_lines[i+1]
            if validate_url(url):
                entry = f"{th_lines[i]}\n{url}"
                valid_th.append(entry)
                categories["TH"].append(entry)

    with open("thailand.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(valid_th))

    # ===== Smart.m3u =====
    smart_lines = fetch_m3u(URL_SMART)
    for i in range(len(smart_lines)):
        if smart_lines[i].startswith("#EXTINF"):
            url = smart_lines[i+1]
            line = smart_lines[i]
            if "衛視" in line and "IPV4" in line.upper():
                categories["WS_V4"].append(f"{line}\n{url}")
            elif "央視" in line and "IPV4" in line.upper():
                categories["YS_V4"].append(f"{line}\n{url}")
            elif any(k in line.upper() for k in ["4K", "8K"]):
                categories["K48"].append(f"{line}\n{url}")

    # ===== YouTube =====
    yt = []
    if os.path.exists(YT_FILE):
        with open(YT_FILE, "r", encoding="utf-8") as f:
            yt = [l.strip() for l in f if l.strip() and not l.startswith("#EXTM3U")]

    # ===== 輸出順序（重複一次）=====
    order = [
        "LITV", "GENERAL", "SPORT", "KIDS", "NEWS", "OTHER", "MUSIC",
        "LITV", "GENERAL", "SPORT", "KIDS", "NEWS", "OTHER", "MUSIC",
        "TH", "WS_V4", "YS_V4", "K48"
    ]

    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if yt:
            f.write("\n".join(yt) + "\n")
        for key in order:
            if categories.get(key):
                f.write("\n".join(categories[key]) + "\n")

    print("✅ 更新完成：4gtv.m3u / thailand.m3u")

if __name__ == "__main__":
    run()