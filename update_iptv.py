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
    """
    不穩定移除機制：
    檢查連結可用性，若 2.5 秒內無回應或非 200 狀態碼則視為不穩定。
    """
    try:
        # 使用 stream=True 僅抓取標頭以節省流量與時間
        with requests.get(url, timeout=2.5, stream=True, allow_redirects=True) as response:
            return response.status_code == 200
    except:
        return False

def run():
    # 來源配置 (已移除 Smart)
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_LINWEI = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
    URL_IPTV_ORG_TH = "https://iptv-org.github.io/iptv/countries/th.m3u"
    YT_FILE = "youtube 新聞.m3u"

    # 初始化分類容器
    categories = {
        "YT": [], "NEWS": [], "GENERAL": [], "HOTEL": [], 
        "OFFY": [], "DRAMA": [], "KIDS": [], "MUSIC": [], 
        "SPORT": [], "OTHER": [], "TH": []
    }

    # 處理 4GTV 與 LinWei 來源
    for src in [URL_4GTV, URL_LINWEI]:
        lines = fetch_m3u(src)
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                info, url = lines[i], lines[i+1].strip() if i+1 < len(lines) else ""
                if not url: continue
                
                # 分類關鍵字匹配
                if any(k in info for k in ["酒店", "HOTEL", "台灣酒店"]): categories["HOTEL"].append(f"{info}\n{url}")
                elif any(k in info for k in ["歐飛", "點播", "OFFY"]): categories["OFFY"].append(f"{info}\n{url}")
                elif any(k in info for k in ["新聞", "財經"]): categories["NEWS"].append(f"{info}\n{url}")
                elif "綜合" in info: categories["GENERAL"].append(f"{info}\n{url}")
                elif any(k in info for k in ["戲劇", "電影", "紀錄"]): categories["DRAMA"].append(f"{info}\n{url}")
                elif any(k in info for k in ["兒童", "少兒", "動漫"]): categories["KIDS"].append(f"{info}\n{url}")
                elif any(k in info for k in ["音樂", "綜藝", "娛樂"]): categories["MUSIC"].append(f"{info}\n{url}")
                elif any(k in info for k in ["體育", "運動", "健康", "生活"]): categories["SPORT"].append(f"{info}\n{url}")
                else: categories["OTHER"].append(f"{info}\n{url}")

    # 處理 Thailand (包含不穩定移除)
    print("正在篩選泰國頻道並移除不穩定源...")
    th_lines = fetch_m3u(URL_IPTV_ORG_TH)
    for i in range(len(th_lines)):
        if th_lines[i].startswith("#EXTINF"):
            info, url = th_lines[i], th_lines[i+1].strip()
            if is_stable(url): 
                categories["TH"].append(f"{info}\n{url}")
    
    # 儲存獨立的 Thailand.m3u
    with open("thailand.m3u", "w", encoding="utf-8") as tf:
        tf.write("#EXTM3U\n" + "\n".join(categories["TH"]))

    # 讀取本地 YouTube
    if os.path.exists(YT_FILE):
        with open(YT_FILE, "r", encoding="utf-8") as yf:
            categories["YT"] = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 寫入最終合併檔案 4gtv.m3u (不包含 Smart 相關分類)
    # 排序：YT -> 新聞 -> 綜合 -> 酒店 -> 歐飛 -> 戲劇 -> 兒童 -> 音樂 -> 運動 -> 其它 -> Thailand
    order = ["YT", "NEWS", "GENERAL", "HOTEL", "OFFY", "DRAMA", "KIDS", "MUSIC", "SPORT", "OTHER", "TH"]
    
    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for key in order:
            if categories[key]:
                unique_list = list(dict.fromkeys(categories[key])) 
                f.write("\n".join(unique_list) + "\n")

    print("✅ 更新完成！已完全移除 Smart 來源並保持列表純淨。")

if __name__ == "__main__":
    run()
