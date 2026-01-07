import requests
import re

def fetch_m3u_content(url):
    """抓取遠端 M3U 內容並回傳行列表"""
    try:
        print(f"正在抓取資源: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text.splitlines()
    except Exception as e:
        print(f"錯誤: 無法讀取來源 {e}")
        return []

def parse_channels(lines):
    """解析 M3U 行，將頻道按分類標籤分組"""
    # 這裡將頻道分為三個目標群組
    groups = {
        "Litv立視": [],
        "亞太GT": [],
        "體育兢技": []
    }
    
    current_info = None
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http") and current_info:
            # 根據頻道資訊中的關鍵字進行分類
            if "Litv" in current_info or "立視" in current_info:
                groups["Litv立視"].append(f"{current_info}\n{line}")
            elif "亞太" in current_info or "GT" in current_info:
                groups["亞太GT"].append(f"{current_info}\n{line}")
            elif any(k in current_info for k in ["體育", "運動", "兢技", "Sport"]):
                groups["體育兢技"].append(f"{current_info}\n{line}")
            current_info = None
            
    return groups

def run():
    # 來源網址
    SOURCE_URL = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
    OUTPUT_FILE = "my_iptv.m3u"
    
    # 1. 抓取資料
    lines = fetch_m3u_content(SOURCE_URL)
    if not lines:
        return

    # 2. 解析與分類
    channel_groups = parse_channels(lines)

    # 3. 按照要求順序排列輸出
    # 順序：1. Litv立視 -> 2. 亞太GT -> 3. 體育兢技
    ordered_keys = ["Litv立視", "亞太GT", "體育兢技"]
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for key in ordered_keys:
            if channel_groups[key]:
                print(f"寫入 {key} 分類，共 {len(channel_groups[key])} 個頻道")
                f.write("\n".join(channel_groups[key]) + "\n")

    print(f"\n✅ 處理完成！檔案已儲存至: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
