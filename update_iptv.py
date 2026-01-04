import requests
import os

def fetch_m3u(url):
    """抓取 M3U 檔案"""
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text.splitlines()
    except Exception as e:
        print(f"無法抓取 {url}: {e}")
        return []

def is_stable(url):
    """檢查連結可用性，2.5 秒超時"""
    try:
        with requests.get(url, timeout=2.5, stream=True, allow_redirects=True) as response:
            return response.status_code == 200
    except:
        return False

def run():
    # 來源配置
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_LINWEI = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
    URL_IPTV_ORG_TH = "https://iptv-org.github.io/iptv/countries/th.m3u"
    YT_FILE = "youtube 新聞.m3u"

    # 定義過濾黑名單（徹底移除這些字眼的頻道）
    BLACKLIST = ["酒店", "HOTEL", "歐飛", "OFFY", "點播"]

    # 初始化分類容器
    categories = {
        "YT": [], "NEWS": [], "GENERAL": [], "DRAMA": [], 
        "KIDS": [], "MUSIC": [], "SPORT": [], "OTHER": [], "TH": []
    }

    # 處理 4GTV 與 LinWei 來源
    for src in [URL_4GTV, URL_LINWEI]:
        lines = fetch_m3u(src)
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                info, url = lines[i], lines[i+1].strip() if i+1 < len(lines) else ""
                if not url: continue
                
                # --- 強制過濾機制：如果在黑名單中，直接跳過 ---
                if any(word in info.upper() for word in BLACKLIST):
                    continue

                # 針對 Smart 關鍵字進行穩定性檢查
                if "smart" in info.lower():
                    if not is_stable(url):
                        continue 

                # 分類邏輯
                if any(k in info for k in ["新聞", "財經"]): categories["NEWS"].append(f"{info}\n{url}")
                elif "綜合" in info: categories["GENERAL"].append(f"{info}\n{url}")
                elif any(k in info for k in ["兒童與青少年",]): categories["KIDS"].append(f"{info}\n{url}")
                elif any(k in info for k in ["戲劇", "電影", "紀錄"]): categories["DRAMA"].append(f"{info}\n{url}")

                elif any(k in info for k in ["音樂", "綜藝", "娛樂"]): categories["MUSIC"].append(f"{info}\n{url}")
                elif any(k in info for k in ["體育", "運動", "健康", "生活"]): categories["SPORT"].append(f"{info}\n{url}")
                else: categories["OTHER"].append(f"{info}\n{url}")

    # 處理 Thailand
    print("正在檢測泰國頻道穩定性...")
    th_lines = fetch_m3u(URL_IPTV_ORG_TH)
    for i in range(len(th_lines)):
        if th_lines[i].startswith("#EXTINF"):
            info, url = th_lines[i], th_lines[i+1].strip()
            if is_stable(url): 
                categories["TH"].append(f"{info}\n{url}")
    
    with open("thailand.m3u", "w", encoding="utf-8") as tf:
        tf.write("#EXTM3U\n" + "\n".join(categories["TH"]))

    # 讀取本地 YouTube
    if os.path.exists(YT_FILE):
        with open(YT_FILE, "r", encoding="utf-8") as yf:
            categories["YT"] = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 寫入最終 4gtv.m3u
    order = ["YT", "NEWS", "GENERAL", "DRAMA", "KIDS", "MUSIC", "SPORT", "OTHER", "TH"]
    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for key in order:
            if categories[key]:
                unique_list = list(dict.fromkeys(categories[key])) 
                f.write("\n".join(unique_list) + "\n")

    print("Cleanup Completed!")

if __name__ == "__main__":
    run()
