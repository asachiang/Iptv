import requests
import re
import os

def fetch_m3u(url):
    """抓取 M3U 檔案"""
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
        # 使用串流模式獲取開頭，驗證連結是否有效
        response = requests.get(url, timeout=3, stream=True)
        return response.status_code == 200
    except:
        return False

def run():
    # 來源網址配置
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    # 新增：LinWei630718 直播源
    URL_LINWEI = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
    # 泰國頻道來源
    URL_IPTV_ORG_TH = "https://iptv-org.github.io/iptv/countries/th.m3u"
    
    YT_FILE = "youtube 新聞.m3u"

    # 初始化分類容器 (依據要求順序)
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

    # 合併多個來源進行處理
    sources = [URL_4GTV, URL_LINWEI]
    
    for source_url in sources:
        print(f"正在處理來源: {source_url}")
        lines = fetch_m3u(source_url)
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url_line = lines[i+1].strip() if i+1 < len(lines) else ""
                
                # 分類關鍵字匹配
                if any(k in info for k in ["新聞", "財經"]): categories["NEWS"].append(f"{info}\n{url_line}")
                elif "綜合" in info: categories["GENERAL"].append(f"{info}\n{url_line}")
                elif any(k in info for k in ["戲劇", "電影", "紀錄"]): categories["DRAMA"].append(f"{info}\n{url_line}")
                elif any(k in info for k in ["兒童", "少兒", "少年", "動漫"]): categories["KIDS"].append(f"{info}\n{url_line}")
                elif any(k in info for k in ["音樂", "綜藝", "娛樂"]): categories["MUSIC"].append(f"{info}\n{url_line}")
                elif any(k in info for k in ["體育", "運動", "健康", "生活"]): categories["SPORT"].append(f"{info}\n{url_line}")
                else: categories["OTHER"].append(f"{info}\n{url_line}")
                i += 2
            else:
                i += 1

    # 處理 Thailand (獨立儲存並過濾)
    print("正在篩選並驗證 Thailand 頻道...")
    th_lines = fetch_m3u(URL_IPTV_ORG_TH)
    valid_th_content = []
    for j, line in enumerate(th_lines):
        if line.startswith("#EXTINF"):
            u = th_lines[j+1].strip()
            if validate_url(u):
                valid_th_content.append(f"{line}\n{u}")
                categories["TH"].append(f"{line}\n{u}")
    
    with open("thailand.m3u", "w", encoding="utf-8") as tf:
        tf.write("#EXTM3U\n" + "\n".join(valid_th_content))

    # 處理 Smart.m3u 中的特殊頻道
    smart_lines = fetch_m3u(URL_SMART)
    for j, line in enumerate(smart_lines):
        if line.startswith("#EXTINF"):
            u = smart_lines[j+1].strip()
            if "衛視" in line and "IPV4" in line.upper(): categories["WS_V4"].append(f"{line}\n{u}")
            elif "央視" in line and "IPV4" in line.upper(): categories["YS_V4"].append(f"{line}\n{u}")
            elif any(k in line.upper() for k in ["4K", "8K"]): categories["K48"].append(f"{line}\n{u}")

    # 讀取 YouTube 新聞
    yt_content = []
    if os.path.exists(YT_FILE):
        with open(YT_FILE, "r", encoding="utf-8") as yf:
            yt_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 依照要求的順序寫入最終檔案 4gtv.m3u
    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        # 1. YouTube
        if yt_content: f.write("\n".join(yt_content) + "\n")
        
        # 2. 依序寫入其他分類
        order = ["NEWS", "GENERAL", "DRAMA", "KIDS", "MUSIC", "SPORT", "OTHER", "TH", "WS_V4", "YS_V4", "K48"]
        for key in order:
            if categories[key]:
                # 去除重複項 (以網址為基準)
                unique_entries = list(dict.fromkeys(categories[key]))
                f.write("\n".join(unique_entries) + "\n")

    print("✅ 腳本執行成功！已整合新直播源並更新 thailand.m3u 與 4gtv.m3u")

if __name__ == "__main__":
    run()
