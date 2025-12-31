import requests
import re
import os

def fetch_m3u(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text.splitlines()

def run():
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    
    # 這裡可以自定義你想要存檔的路徑
    OUTPUT_SMART_FILE = "smart.m3u" 
    OUTPUT_4GTV_FILE = "4gtv.m3u"
    youtube_file = "youtube 新聞.m3u"

    PREFERRED_ORDER = [
        "財經新聞", "新聞", "綜合",
        "戲劇、電影", "電影", "戲劇",
        "兒童", "其他"
    ]

    try:
        # ========= 1️⃣ 抓取與儲存 Smart M3U =========
        # 這是你要求的：獲取 smart 並獨立存檔
        smart_lines = fetch_m3u(URL_SMART)
        with open(OUTPUT_SMART_FILE, "w", encoding="utf-8") as sf:
            sf.write("\n".join(smart_lines))
        print(f"✅ 已成功同步 smart.m3u 至本地")

        # 為了後續合併，提取 smart 內容
        smart_content = []
        i = 0
        while i < len(smart_lines):
            line = smart_lines[i].strip()
            if line.startswith("#EXTINF"):
                smart_content.append(f"{line}\n{smart_lines[i + 1].strip()}")
                i += 2
            else:
                i += 1

        # ========= 2️⃣ 抓取 4GTV 並分類 =========
        lines = fetch_m3u(URL_4GTV)
        groups = {name: [] for name in PREFERRED_ORDER}
        header = "#EXTM3U"

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                match = re.search(r'group-title="([^"]+)"', info)
                detected = match.group(1) if match else "其他"

                key = "其他"
                for k in PREFERRED_ORDER:
                    if k in detected:
                        key = k
                        break
                groups[key].append(f"{info}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

        # ========= 3️⃣ 讀取 YouTube 新聞 =========
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                for line in yf:
                    if not line.startswith("#EXTM3U") and line.strip():
                        youtube_content.append(line.strip())

        # ========= 4️⃣ 寫入合併後的 4gtv.m3u =========
        with open(OUTPUT_4GTV_FILE, "w", encoding="utf-8") as f:
            f.write(header + "\n")
            # YouTube 置頂
            for line in youtube_content:
                f.write(line + "\n")
            # 4GTV 分類
            for cat in PREFERRED_ORDER:
                for entry in groups[cat]:
                    f.write(entry + "\n")
            # Smart 追加
            for entry in smart_content:
                f.write(entry + "\n")

        print(f"✅ 成功：所有頻道已合併至 {OUTPUT_4GTV_FILE}")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    run()
