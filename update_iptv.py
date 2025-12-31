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
    
    # 這是你的本地 YouTube 檔案
    youtube_file = "youtube 新聞.m3u"

    # 定義 4GTV 的排序順序
    PREFERRED_ORDER = [
        "財經新聞", "新聞", "綜合",
        "戲劇、電影", "電影", "戲劇",
        "兒童", "其他"
    ]
    
    # 【新增】定義 smart.m3u 想要保留的關鍵字
    SMART_FILTER = ["台灣", "香港", "泰國"]

    try:
        # ========= 1️⃣ 抓取 4GTV 分類內容 =========
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

        # ========= 2️⃣ 讀取 YouTube 新聞 =========
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                for line in yf:
                    if not line.startswith("#EXTM3U") and line.strip():
                        youtube_content.append(line.strip())

        # ========= 3️⃣ 抓取 smart.m3u 並進行過濾 =========
        smart_lines = fetch_m3u(URL_SMART)
        
        # 【修改】這裡同時做兩件事：1.存成原始檔，2.篩選後準備合併
        # 儲存原始檔案到你的 GitHub
        with open("smart.m3u", "w", encoding="utf-8") as sf:
            sf.write("\n".join(smart_lines))
        
        filtered_smart_content = []
        i = 0
        while i < len(smart_lines):
            line = smart_lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url_line = smart_lines[i + 1].strip() if i + 1 < len(smart_lines) else ""
                
                # 【關鍵】檢查這一行是否包含 台灣、香港 或 泰國
                if any(keyword in info for keyword in SMART_FILTER):
                    filtered_smart_content.append(f"{info}\n{url_line}")
                i += 2
            else:
                i += 1

        # ========= 4️⃣ 寫入最終合併的 4gtv.m3u =========
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")

            # A. YouTube 新聞置頂
            for line in youtube_content:
                f.write(line + "\n")

            # B. 篩選後的 Smart 頻道（放第 2, 3, 4 順位感官）
            for entry in filtered_smart_content:
                f.write(entry + "\n")

            # C. 4GTV 原分類（放後面）
            for cat in PREFERRED_ORDER:
                for entry in groups[cat]:
                    f.write(entry + "\n")

        print("✅ 成功：已篩選 smart.m3u 並合併至 4gtv.m3u")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    run()
