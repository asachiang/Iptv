import requests
import re
import os

def fetch_m3u(url):
    """抓取網路上的 M3U 檔案"""
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text.splitlines()

def run():
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    youtube_file = "youtube 新聞.m3u"
    
    PREFERRED_ORDER = ["新聞", "財經新聞", "綜合", "戲劇、電影", "電影", "戲劇", "兒童", "其他"]

    try:
        # ========= 1️⃣ 處理 4GTV 分類 =========
        lines = fetch_m3u(URL_4GTV)
        groups = {name: [] for name in PREFERRED_ORDER}
        header = "#EXTM3U"
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info, url_line = line, (lines[i+1].strip() if i+1 < len(lines) else "")
                match = re.search(r'group-title="([^"]+)"', info)
                detected = match.group(1) if match else "其他"
                key = next((k for k in PREFERRED_ORDER if k in detected), "其他")
                groups[key].append(f"{info}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"): header = line
                i += 1

        # ========= 2️⃣ 讀取 YouTube 新聞 =========
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                youtube_content = [line.strip() for line in yf if not line.startswith("#EXTM3U") and line.strip()]

        

        # ========= 4️⃣ 寫入合併後的 4gtv.m3u =========
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            # 1. YouTube
            for line in youtube_content: f.write(line + "\n")
            # 2. 4GTV 新聞/財經/綜合 (優先)
            priority_cats = ["新聞", "財經新聞", "綜合"]
            for cat in priority_cats:
                for entry in groups[cat]: f.write(entry + "\n")
            # 3. GPT 台、港、泰
            for entry in smart_tw: f.write(entry + "\n")
            for entry in smart_hk: f.write(entry + "\n")
            for entry in smart_th: f.write(entry + "\n")
            # 4. 剩餘分類
            for cat in PREFERRED_ORDER:
                if cat not in priority_cats:
                    for entry in groups[cat]: f.write(entry + "\n")

        print("✅ 檔案已成功更新並儲存")
    except Exception as e:
        print(f"❌ 錯誤：{e}")

if __name__ == "__main__":
    run()
