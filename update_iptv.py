import requests
import re
import os

def fetch_m3u(url):
    """抓取網路上的 M3U 檔案"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text.splitlines()
    except Exception as e:
        print(f"❌ 無法抓取來源 {url}: {e}")
        return []

def run():
    # 1. 定義來源
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    # 您可以視需求增加其他 IPv4 來源 URL
    OTHER_SOURCES = [
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    YOUTUBE_FILE = "youtube 新聞.m3u"
    OUTPUT_FILE = "4gtv.m3u"
    
    # 2. 定義要求的排序 (Key 對應 M3U 中的 group-title 關鍵字)
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞",
        "新聞財經",
        "綜合",
        "央视IPV4",
        "衛視IPV4",
        "4K8K頻道",
        "歷年春晚",
        "戲劇、電影與紀錄片",
        "兒童與青少年",
        "音樂綜藝",
        "運動健康生活"
    ]
    
    # 初始化分類容器
    groups = {name: [] for name in PREFERRED_ORDER}
    groups["其他"] = [] # 備用分類
    header = "#EXTM3U"

    # --- 步驟 A: 處理 4GTV 與其他網路來源 ---
    all_urls = [{"name": "4GTV", "url": URL_4GTV}] + OTHER_SOURCES
    
    for src in all_urls:
        print(f"正在處理: {src['name']}...")
        lines = fetch_m3u(src['url'])
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                url_line = lines[i+1].strip() if i+1 < len(lines) else ""
                
                # 獲取 group-title
                match = re.search(r'group-title="([^"]+)"', info_line)
                detected_group = match.group(1) if match else ""
                
                # 分類邏輯判斷
                target_key = "其他"
                
                # 根據您的新排序規則進行關鍵字匹配
                if any(k in detected_group for k in ["新聞", "財經"]):
                    target_key = "新聞財經"
                elif any(k in detected_group for k in ["綜合", "General"]):
                    target_key = "綜合"
                elif "CCTV" in detected_group or "央視" in detected_group:
                    target_key = "央视IPV4"
                elif "衛視" in detected_group:
                    target_key = "衛視IPV4"
                elif any(k in detected_group for k in ["4K", "8K", "Ultra"]):
                    target_key = "4K8K頻道"
                elif "春晚" in detected_group:
                    target_key = "歷年春晚"
                elif any(k in detected_group for k in ["戲劇", "電影", "紀錄片", "Movie", "Drama"]):
                    target_key = "戲劇、電影與紀錄片"
                elif any(k in detected_group for k in ["兒童", "青少年", "Kids", "Cartoon"]):
                    target_key = "兒童與青少年"
                elif any(k in detected_group for k in ["音樂", "綜藝", "Music", "Variety"]):
                    target_key = "音樂綜藝"
                elif any(k in detected_group for k in ["運動", "健康", "生活", "Sports", "Health"]):
                    target_key = "運動健康生活"

                groups[target_key].append(f"{info_line}\n{url_line}")
                i += 2
            else:
                i += 1

    # --- 步驟 B: 讀取本地 YouTube 新聞 ---
    youtube_content = []
    if os.path.exists(YOUTUBE_FILE):
        print(f"正在加載本地檔案: {YOUTUBE_FILE}")
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            # 過濾掉標頭，保留內容
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # --- 步驟 C: 依照指定順序寫入最終檔案 ---
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")

        # 1. 寫入 YouTube 新聞
        print("寫入分類: YOUTUBE油管新聞")
        for line in youtube_content:
            f.write(line + "\n")

        # 2. 依序寫入其他分類
        for category in PREFERRED_ORDER:
            if category == "YOUTUBE油管新聞": continue # 已寫入
            
            if groups[category]:
                print(f"寫入分類: {category}")
                for entry in groups[category]:
                    f.write(entry + "\n")
        
        # 3. 寫入未被分類的內容
        if groups["其他"]:
            for entry in groups["其他"]:
                f.write(entry + "\n")

    print(f"\n✅ 整合完成！檔案已儲存至: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
