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
    # 1. 來源定義
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    YOUTUBE_FILE = "youtube 新聞.m3u"
    OUTPUT_FILE = "4gtv.m3u"
    
    # 2. 嚴格排序順序
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
    
    groups = {name: [] for name in PREFERRED_ORDER}
    groups["其他"] = []
    header = "#EXTM3U"

    for src in sources:
        print(f"正在分析來源: {src['name']}")
        lines = fetch_m3u(src['url'])
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                # 抓取下方所有直到下一個 #EXTINF 之前的內容，確保多行網址或標籤不遺失
                url_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].startswith("#EXTINF"):
                    if lines[j].strip():
                        url_lines.append(lines[j].strip())
                    j += 1
                
                content = "\n".join(url_lines)
                
                # 獲取標籤與頻道名進行分類判斷
                match = re.search(r'group-title="([^"]+)"', info_line)
                group_tag = match.group(1).upper() if match else ""
                chan_name = info_line.split(',')[-1].upper()
                search_scope = group_tag + chan_name
                
                target_key = "其他"
                
                # 分類判斷邏輯（優化關鍵字）
                if any(k in search_scope for k in ["CCTV", "央視", "央视", "CGTN"]):
                    target_key = "央视IPV4"
                elif any(k in search_scope for k in ["衛視", "卫视", "TVB", "翡翠", "鳳凰", "PHOENIX", "HK", "香港"]):
                    target_key = "衛視IPV4"
                elif any(k in search_scope for k in ["4K", "8K", "UHD", "ULTRA"]):
                    target_key = "4K8K頻道"
                elif "春晚" in search_scope:
                    target_key = "歷年春晚"
                elif any(k in search_scope for k in ["新聞", "NEWS", "財經", "FINANCE", "東森", "三立", "TVBS"]):
                    target_key = "新聞財經"
                elif any(k in search_scope for k in ["綜合", "GENERAL", "4GTV", "民視", "台視", "中視", "華視"]):
                    target_key = "綜合"
                elif any(k in search_scope for k in ["電影", "戲劇", "劇", "MOVIE", "DRAMA", "DOCUMENTARY", "紀錄"]):
                    target_key = "戲劇、電影與紀錄片"
                elif any(k in search_scope for k in ["兒童", "少兒", "KIDS", "CARTOON", "動漫", "ANIMAX", "NICKELODEON", "DISNEY"]):
                    target_key = "兒童與青少年"
                elif any(k in search_scope for k in ["音樂", "綜藝", "MUSIC", "VARIETY", "娛樂"]):
                    target_key = "音樂綜藝"
                elif any(k in search_scope for k in ["運動", "體育", "SPORTS", "健康", "生活", "HEALTH", "博斯", "愛爾達"]):
                    target_key = "運動健康生活"
                
                # 重新修正 group-title 標籤
                new_info = re.sub(r'group-title="[^"]+"', f'group-title="{target_key}"', info_line)
                if 'group-title=' not in new_info:
                    new_info = new_info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_key}"')
                
                groups[target_key].append(f"{new_info}\n{content}")
                i = j
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

    # 3. 讀取本地 YouTube
    youtube_content = []
    if os.path.exists(YOUTUBE_FILE):
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 4. 寫入最終檔案
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        
        # A. YOUTUBE
        for line in youtube_content:
            f.write(line + "\n")
            
        # B. 依序分類
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for item in groups[cat]:
                f.write(item + "\n")

    print(f"✅ 修正完成！已保留原始連接並優化分類。")

if __name__ == "__main__":
    run()
