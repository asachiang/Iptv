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
        print(f"抓取失敗 {url}: {e}")
        return []

def run():
    # 來源設定
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    YOUTUBE_FILE = "youtube 新聞.m3u"
    OUTPUT_FILE = "4gtv.m3u"
    
    # 嚴格定義排序與分類名稱
    # 這是最終 M3U 檔案中的 group-title 順序
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
    groups["其他"] = []
    header = "#EXTM3U"

    # 1. 處理 4GTV 網路來源
    print("正在抓取 4GTV 來源...")
    lines = fetch_m3u(URL_4GTV)
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            info_line = line
            url_line = lines[i+1].strip() if i+1 < len(lines) else ""
            
            # 取得原始頻道資訊中的分組關鍵字
            match = re.search(r'group-title="([^"]+)"', info_line)
            detected = match.group(1) if match else ""
            
            # 判定應歸類到哪個 PREFERRED_ORDER
            target_key = "其他"
            
            if any(k in detected for k in ["新聞", "財經"]):
                target_key = "新聞財經"
            elif any(k in detected for k in ["綜合", "General"]):
                target_key = "綜合"
            elif any(k in detected for k in ["CCTV", "央視", "央视"]):
                target_key = "央视IPV4"
            elif any(k in detected for k in ["衛視", "卫视"]):
                target_key = "衛視IPV4"
            elif any(k in detected for k in ["4K", "8K", "超高清", "UHD"]):
                target_key = "4K8K頻道"
            elif "春晚" in detected:
                target_key = "歷年春晚"
            elif any(k in detected for k in ["戲劇", "電影", "紀錄片", "Movie", "Drama", "紀錄"]):
                target_key = "戲劇、電影與紀錄片"
            elif any(k in detected for k in ["兒童", "少兒", "卡通", "Kids", "動漫"]):
                target_key = "兒童與青少年"
            elif any(k in detected for k in ["音樂", "綜藝", "Music", "Variety", "娛樂"]):
                target_key = "音樂綜藝"
            elif any(k in detected for k in ["運動", "健康", "生活", "體育", "Sports", "休閒"]):
                target_key = "運動健康生活"
            
            # 統一修改標籤名稱並存入組別
            updated_info = re.sub(r'group-title="[^"]+"', f'group-title="{target_key}"', info_line)
            groups[target_key].append(f"{updated_info}\n{url_line}")
            i += 2
        else:
            if line.startswith("#EXTM3U"):
                header = line
            i += 1

    # 2. 處理本地 YouTube 新聞
    youtube_content = []
    if os.path.exists(YOUTUBE_FILE):
        print(f"載入本地檔案: {YOUTUBE_FILE}")
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            # 只保留內容，去掉對方的 #EXTM3U 標頭
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 3. 依照指定順序寫入檔案
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")

        # A. 第一順位：YOUTUBE油管新聞
        for entry in youtube_content:
            f.write(entry + "\n")

        # B. 依照 PREFERRED_ORDER 的順序寫入
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for item in groups[cat]:
                f.write(item + "\n")

        # C. 最後寫入沒被分類到的
        for item in groups["其他"]:
            f.write(item + "\n")

    print(f"✅ 腳本執行成功！已輸出排序後的 {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
