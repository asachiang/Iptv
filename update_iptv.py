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
        print(f"❌ 抓取失敗 {url}: {e}")
        return []

def run():
    # 1. 來源定義 (已整合您指定的所有來源)
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    YOUTUBE_FILE = "youtube 新聞.m3u"
    OUTPUT_FILE = "4gtv.m3u"
    
    # 2. 您要求的嚴格排序清單
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

    # --- 步驟 A: 處理網路來源 ---
    for src in sources:
        print(f"正在處理: {src['name']}")
        lines = fetch_m3u(src['url'])
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                url_line = lines[i+1].strip() if i+1 < len(lines) else ""
                
                # 取得頻道名稱 (逗號後面的文字) 作為判斷依據
                chan_name = info_line.split(',')[-1].upper()
                
                # 強制關鍵字分類邏輯
                target_key = "其他"
                
                if any(k in chan_name for k in ["CCTV", "央視", "央视"]):
                    target_key = "央视IPV4"
                elif any(k in chan_name for k in ["衛視", "卫视", "TVB", "翡翠", "鳳凰", "PHOENIX", "HONG KONG", "HK"]):
                    target_key = "衛視IPV4"
                elif any(k in chan_name for k in ["4K", "8K", "UHD"]):
                    target_key = "4K8K頻道"
                elif "春晚" in chan_name:
                    target_key = "歷年春晚"
                elif any(k in chan_name for k in ["新聞", "NEWS", "財經", "FINANCE"]):
                    target_key = "新聞財經"
                elif any(k in chan_name for k in ["綜合", "GENERAL", "4GTV"]):
                    target_key = "綜合"
                elif any(k in chan_name for k in ["電影", "戲劇", "劇", "MOVIE", "DRAMA", "DOCUMENTARY", "紀錄"]):
                    target_key = "戲劇、電影與紀錄片"
                elif any(k in chan_name for k in ["兒童", "少兒", "KIDS", "CARTOON", "動漫", "ANIMAX"]):
                    target_key = "兒童與青少年"
                elif any(k in chan_name for k in ["音樂", "綜藝", "MUSIC", "VARIETY", "娛樂"]):
                    target_key = "音樂綜藝"
                elif any(k in chan_name for k in ["運動", "體育", "SPORTS", "健康", "生活", "HEALTH"]):
                    target_key = "運動健康生活"
                
                # 重新標記 group-title 為目標分類名
                info_line = re.sub(r'group-title="[^"]+"', f'group-title="{target_key}"', info_line)
                if 'group-title=' not in info_line:
                    info_line = info_line.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_key}"')
                
                groups[target_key].append(f"{info_line}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

    # --- 步驟 B: 處理本地 YouTube ---
    youtube_content = []
    if os.path.exists(YOUTUBE_FILE):
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # --- 步驟 C: 依序寫入 (確保檔案內容順序符合您的要求) ---
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")

        # 1. 第一順位：YouTube 新聞
        for line in youtube_content:
            f.write(line + "\n")

        # 2. 依照 PREFERRED_ORDER 順序寫入各分類頻道
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            if groups[cat]:
                for item in groups[cat]:
                    f.write(item + "\n")

        # 3. 最後才寫入剩下的「其他」頻道
        for item in groups["其他"]:
            f.write(item + "\n")

    print(f"✅ 更新完成！輸出檔案：{OUTPUT_FILE}")

if __name__ == "__main__":
    run()
