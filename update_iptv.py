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
    # 1. 定義來源 (請在此處填入包含央視、衛視、4K 的網址)
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    
    # [span_2](start_span)您可以在此清單加入更多來源網址[span_2](end_span)
    OTHER_SOURCES = [
        "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/CNTV.m3u", # 範例：央視衛視源
        "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u"  # 範例：通用源
    ]
    
    YOUTUBE_FILE = "youtube 新聞.m3u"
    OUTPUT_FILE = "4gtv.m3u"
    
    # 2. [span_3](start_span)[span_4](start_span)定義排序順序[span_3](end_span)[span_4](end_span)
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

    # --- 步驟 A: 處理所有網路來源 ---
    [span_5](start_span)all_urls = [URL_4GTV] + OTHER_SOURCES[span_5](end_span)
    
    for url in all_urls:
        print(f"正在抓取來源: {url}")
        [span_6](start_span)lines = fetch_m3u(url)[span_6](end_span)
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                [span_7](start_span)url_line = lines[i+1].strip() if i+1 < len(lines) else ""[span_7](end_span)
                
                # [span_8](start_span)取得 group-title 或頻道名稱進行判斷[span_8](end_span)
                match = re.search(r'group-title="([^"]+)"', info_line)
                detected = match.group(1) if match else ""
                
                # 為了增加準確度，也檢查頻道名稱 (tvg-name 或最後的逗號後)
                chan_name = info_line.split(',')[-1]
                search_text = detected + chan_name
                
                target_key = "其他"
                
                # 強制分類邏輯
                if any(k in search_text for k in ["CCTV", "央視", "央视"]):
                    target_key = "央视IPV4"
                elif any(k in search_text for k in ["衛視", "卫视"]):
                    target_key = "衛視IPV4"
                elif any(k in search_text for k in ["4K", "8K", "超高清", "UHD"]):
                    target_key = "4K8K頻道"
                elif "春晚" in search_text:
                    target_key = "歷年春晚"
                elif any(k in search_text for k in ["新聞", "財經"]):
                    target_key = "新聞財經"
                elif any(k in search_text for k in ["綜合", "General"]):
                    target_key = "綜合"
                elif any(k in search_text for k in ["戲劇", "電影", "紀錄片", "Movie", "Drama"]):
                    target_key = "戲劇、電影與紀錄片"
                elif any(k in search_text for k in ["兒童", "少兒", "卡通", "Kids"]):
                    target_key = "兒童與青少年"
                elif any(k in search_text for k in ["音樂", "綜藝", "Music", "Variety"]):
                    target_key = "音樂綜藝"
                elif any(k in search_text for k in ["運動", "健康", "生活", "體育", "Sports"]):
                    target_key = "運動健康生活"
                
                # [span_9](start_span)重新標記分組名稱[span_9](end_span)
                updated_info = re.sub(r'group-title="[^"]+"', f'group-title="{target_key}"', info_line)
                if 'group-title=' not in updated_info:
                    updated_info = updated_info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_key}"')
                
                [span_10](start_span)[span_11](start_span)groups[target_key].append(f"{updated_info}\n{url_line}")[span_10](end_span)[span_11](end_span)
                i += 2
            else:
                i += 1

    # -[span_12](start_span)-- 步驟 B: 處理本地 YouTube ---[span_12](end_span)
    youtube_content = []
    if os.path.exists(YOUTUBE_FILE):
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # -[span_13](start_span)-- 步驟 C: 寫入檔案 (嚴格排序) ---[span_13](end_span)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        [span_14](start_span)f.write(header + "\n")[span_14](end_span)

        # 1. 油管新聞
        for entry in youtube_content:
            f.write(entry + "\n")

        # 2. [span_15](start_span)依照 PREFERRED_ORDER 順序寫入[span_15](end_span)
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for item in groups[cat]:
                f.write(item + "\n")

    print(f"✅ 整合完成！已依照您的順序產出 {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
