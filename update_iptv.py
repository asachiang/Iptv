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
    # 只保留 4GTV 來源
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    youtube_file = "youtube 新聞.m3u"
    
    # 4GTV 分類排序清單
    PREFERRED_ORDER = ["新聞", "財經新聞", "綜合", "戲劇、電影", "電影", "戲劇", "兒童", "其他"]

    try:
        # ========= 1️⃣ 處理 4GTV 內容並分類 =========
        lines = fetch_m3u(URL_4GTV)
        groups = {name: [] for name in PREFERRED_ORDER}
        header = "#EXTM3U"
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url_line = lines[i+1].strip() if i+1 < len(lines) else ""
                match = re.search(r'group-title="([^"]+)"', info)
                detected = match.group(1) if match else "其他"
                # 判斷屬於哪個分類
                key = next((k for k in PREFERRED_ORDER if k in detected), "其他")
                groups[key].append(f"{info}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"): header = line
                i += 1

        # ========= 2️⃣ 讀取本地 YouTube 新聞 =========
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                youtube_content = [line.strip() for line in yf if not line.startswith("#EXTM3U") and line.strip()]

        # ========= 3️⃣ 寫入最終 4gtv.m3u (回歸最穩定的排序) =========
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")

            # A. YouTube 新聞 (最頂端)
            for line in youtube_content:
                f.write(line + "\n")

            # B. 4GTV 依序寫入 (新聞、財經會排在最前面)
            for cat in PREFERRED_ORDER:
                for entry in groups[cat]:
                    f.write(entry + "\n")

        print("✅ 腳本已完成更新：已移除 smart.m3u 相關邏輯。")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    run()
