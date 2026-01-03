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
    # 設定來源網址
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    
    # 本地檔案
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

        # ========= 3️⃣ 抓取 smart.m3u 並分區過濾 =========
        smart_lines = fetch_m3u(URL_SMART)
        
        # 【功能：儲存原始檔到 GitHub 網下】
        with open("smart.m3u", "w", encoding="utf-8") as sf:
            sf.write("\n".join(smart_lines))
        
        # 準備三個籃子裝不同地區的 GPT 頻道
        smart_tw, smart_hk, smart_th = [], [], []

        i = 0
        while i < len(smart_lines):
            line = smart_lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url_line = smart_lines[i+1].strip() if i+1 < len(smart_lines) else ""
                
                # 判定地區 (包含繁簡體關鍵字)
                if any(k in info for k in ["GPT-台湾", "GPT-台灣"]):
                    smart_tw.append(f"{info}\n{url_line}")
                elif "GPT-香港" in info:
                    smart_hk.append(f"{info}\n{url_line}")
                elif any(k in info for k in ["GPT-泰国", "GPT-泰國"]):
                    smart_th.append(f"{info}\n{url_line}")
                i += 2
            else:
                i += 1

        # ========= 4️⃣ 寫入最終合併後的 4gtv.m3u (自定義排序) =========
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")

            # A. YouTube 新聞 (最頂端)
            for line in youtube_content:
                f.write(line + "\n")

            # B. 4GTV 新聞/財經/綜合 (第二、三列順位)
            # 在這裡我們優先寫入這三類
            priority_cats = ["新聞", "財經新聞", "綜合"]
            for cat in priority_cats:
                for entry in groups[cat]:
                    f.write(entry + "\n")

            # C. GPT 地區頻道 (台 > 港 > 泰)
            for entry in smart_tw: f.write(entry + "\n")
            for entry in smart_hk: f.write(entry + "\n")
            for entry in smart_th: f.write(entry + "\n")

            # D. 剩餘的 4GTV 分類 (排除掉前面已寫過的)
            for cat in PREFERRED_ORDER:
                if cat not in priority_cats:
                    for entry in groups[cat]:
                        f.write(entry + "\n")

        print("✅ 腳本執行成功！4gtv.m3u 與 smart.m3u 已同步更新。")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    run()
