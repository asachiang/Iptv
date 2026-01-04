import requests
import re
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
    """檢查連結是否可用 (3秒超時)"""
    try:
        # 使用 GET 請求前幾個位元組來確認是否能播放，比 HEAD 更準確
        response = requests.get(url, timeout=3, stream=True)
        return response.status_code == 200
    except:
        return False

def run():
    # 來源配置
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    URL_IPTV_ORG_TH = "https://iptv-org.github.io/iptv/countries/th.m3u"
    YT_FILE = "youtube 新聞.m3u"

    # 初始化分類容器
    categories = {
        "NEWS": [],      # 新聞財經
        "GENERAL": [],   # 綜合
        "DRAMA": [],     # 戲劇、電影與紀錄片
        "KIDS": [],      # 兒童與青少年
        "MUSIC": [],     # 音樂綜藝
        "SPORT": [],     # 運動健康生活
        "OTHER": [],     # 其它
        "TH": [],        # Thailand
        "WS_V4": [],     # 衛視IPV4
        "YS_V4": [],     # 央視IPV4
        "K48": []        # 4K8K頻道
    }

    # 1. 處理 4GTV
    lines_4gtv = fetch_m3u(URL_4GTV)
    i = 0
    while i < len(lines_4gtv):
        line = lines_4gtv[i].strip()
        if line.startswith("#EXTINF"):
            info, url_line = line, lines_4gtv[i+1].strip()
            # 關鍵字分類邏輯
            if any(k in info for k in ["新聞", "財經"]): categories["NEWS"].append(f"{info}\n{url_line}")
            elif "綜合" in info: categories["GENERAL"].append(f"{info}\n{url_line}")
            elif any(k in info for k in ["戲劇", "電影", "紀錄"]): categories["DRAMA"].append(f"{info}\n{url_line}")
            elif any(k in info for k in ["兒童", "少兒", "動漫"]): categories["KIDS"].append(f"{info}\n{url_line}")
            elif any(k in info for k in ["音樂", "綜藝", "娛樂"]): categories["MUSIC"].append(f"{info}\n{url_line}")
            elif any(k in info for k in ["體育", "運動", "健康", "生活"]): categories["SPORT"].append(f"{info}\n{url_line}")
            else: categories["OTHER"].append(f"{info}\n{url_line}")
            i += 2
        else: i += 1

    # 2. 處理 Thailand (嚴格篩選)
    print("正在篩選 Thailand 頻道...")
    th_lines = fetch_m3u(URL_IPTV_ORG_TH)
    valid_th = []
    for j, line in enumerate(th_lines):
        if line.startswith("#EXTINF"):
            url = th_lines[j+1].strip()
            if validate_url(url):
                valid_th.append(f"{line}\n{url}")
                categories["TH"].append(f"{line}\n{url}")
    
    with open("thailand.m3u", "w", encoding="utf-8") as tf:
        tf.write("#EXTM3U\n" + "\n".join(valid_th))

    # 3. 處理 Smart.m3u (衛視、央視、4K)
    smart_lines = fetch_m3u(URL_SMART)
    for j, line in enumerate(smart_lines):
        if line.startswith("#EXTINF"):
            url = smart_lines[j+1].strip()
            if "衛視" in line and "IPV4" in line.upper(): categories["WS_V4"].append(f"{line}\n{url}")
            elif "央視" in line and "IPV4" in line.upper(): categories["YS_V4"].append(f"{line}\n{url}")
            elif any(k in line.upper() for k in ["4K", "8K"]): categories["K48"].append(f"{line}\n{url}")

    # 4. 讀取 YouTube 新聞
    yt_content = []
    if os.path.exists(YT_FILE):
        with open(YT_FILE, "r", encoding="utf-8") as yf:
            yt_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 5. 合併寫入 4gtv.m3u
    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("\n".join(yt_content) + "\n") # YouTube
        for key in ["NEWS", "GENERAL", "DRAMA", "KIDS", "MUSIC", "SPORT", "OTHER", "TH", "WS_V4", "YS_V4", "K48"]:
            if categories[key]:
                f.write("\n".join(categories[key]) + "\n")

    print("✅ 檔案處理完成：4gtv.m3u, thailand.m3u")

if __name__ == "__main__":
    run()
