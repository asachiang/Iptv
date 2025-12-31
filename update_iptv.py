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
    youtube_file = "youtube 新聞.m3u"

    # 4GTV 的內部分類排序
    PREFERRED_ORDER = ["財經新聞", "新聞", "綜合", "戲劇、電影", "電影", "戲劇", "兒童", "其他"]

    try:
        # ========= 1️⃣ 處理 4GTV 內容 =========
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

        # ========= 3️⃣ 抓取 smart.m3u 並【分地區】儲存 =========
        smart_lines = fetch_m3u(URL_SMART)
        # 同步儲存原始檔到 GitHub
        with open("smart.m3u", "w", encoding="utf-8") as sf:
            sf.write("\n".join(smart_lines))
        
        # 準備三個籃子裝不同地區
        smart_tw, smart_hk, smart_th = [], [], []

        i = 0
        while i < len(smart_lines):
            line = smart_lines[i].strip()
            if line.startswith("#EXTINF"):
                info, url_line = line, (smart_lines[i+1].strip() if i+1 < len(smart_lines) else "")
                # 判定地區 (包含簡體字比對)
                if any(k in info for k in ["GPT-台湾", "GPT-台灣"]):
                    smart_tw.append(f"{info}\n{url_line}")
                elif "GPT-香港" in info:
                    smart_hk.append(f"{info}\n{url_line}")
                elif any(k in info for k in ["GPT-泰国", "GPT-泰國"]):
                    smart_th.append(f"{info}\n{url_line}")
                i += 2
            else: i += 1

                # ========= 4️⃣ 寫入 4gtv.m3u (自定義精細順序) =========
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")

            # [順位 1] YouTube 新聞
            for line in youtube_content: 
                f.write(line + "\n")

            # [順位 2] 4GTV 的「新聞」與「財經新聞」
            # 這樣這兩類就會排在最前面
            for cat in ["新聞", "財經新聞", "綜合"]:
                if cat in groups:
                    for entry in groups[cat]:
                        f.write(entry + "\n")

            # [順位 3] GPT 系列 (台、港、泰)
            for entry in smart_tw: f.write(entry + "\n")
            for entry in smart_hk: f.write(entry + "\n")
            for entry in smart_th: f.write(entry + "\n")

            # [順位 4] 剩餘的 4GTV 分類
            # 我們要避開剛才已經寫過的新聞、財經和綜合
            for cat in PREFERRED_ORDER:
                if cat not in ["新聞", "財經新聞", "綜合"]:
                    for entry in groups[cat]:
                        f.write(entry + "\n")

        print("✅ 成功：已按 台灣 > 香港 > 泰國 順序更新合併檔")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    run()
