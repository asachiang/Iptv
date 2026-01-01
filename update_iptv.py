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
    # 1. [span_0](start_span)定義來源[span_0](end_span)
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    YOUTUBE_FILE = "youtube 新聞.m3u"
    OUTPUT_FILE = "4gtv.m3u"
    
    # 2. [span_1](start_span)您的排序要求[span_1](end_span)
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
        print(f"正在處理來源: {src['name']}")
        lines = fetch_m3u(src['url'])
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                # [span_2](start_span)抓取該頻道後續所有內容，直到下一個 #EXTINF 之前，確保保留所有原始連結參數[span_2](end_span)
                content_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].startswith("#EXTINF"):
                    if lines[j].strip():
                        content_lines.append(lines[j].strip())
                    j += 1
                
                full_content = "\n".join(content_lines)
                
                # [span_3](start_span)取得頻道名稱與原始分類[span_3](end_span)
                chan_name = info_line.split(',')[-1].upper()
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                original_group = group_match.group(1).upper() if group_match else ""
                
                search_text = chan_name + original_group
                target_key = "其他"

                # 分類判定邏輯
                if any(k in search_text for k in ["CCTV", "央視", "央视", "CGTN"]):
                    target_key = "央视IPV4"
                elif any(k in search_text for k in ["衛視", "卫视", "TVB", "翡翠", "鳳凰", "HK", "HONGKONG"]):
                    target_key = "衛視IPV4"
                elif any(k in search_text for k in ["4K", "8K", "UHD", "ULTRA"]):
                    target_key = "4K8K頻道"
                elif "春晚" in search_text:
                    target_key = "歷年春晚"
                elif any(k in search_text for k in ["新聞", "NEWS", "財經"]):
                    target_key = "新聞財經"
                elif any(k in search_text for k in ["綜合", "GENERAL", "4GTV"]):
                    target_key = "綜合"
                elif any(k in search_text for k in ["電影", "戲劇", "MOVIE", "DRAMA"]):
                    target_key = "戲劇、電影與紀錄片"
                elif any(k in search_text for k in ["兒童", "KIDS", "CARTOON"]):
                    target_key = "兒童與青少年"
                elif any(k in search_text for k in ["音樂", "綜藝", "MUSIC", "VARIETY"]):
                    target_key = "音樂綜藝"
                elif any(k in search_text for k in ["運動", "SPORTS", "健康"]):
                    target_key = "運動健康生活"

                # [span_4](start_span)強制更新標籤，使 App 顯示正確分類[span_4](end_span)
                if 'group-title="' in info_line:
                    info_line = re.sub(r'group-title="[^"]+"', f'group-title="{target_key}"', info_line)
                else:
                    info_line = info_line.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_key}"')

                groups[target_key].append(f"{info_line}\n{full_content}")
                i = j
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

    # 3. [span_5](start_span)處理本地 YouTube[span_5](end_span)
    youtube_content = []
    if os.path.exists(YOUTUBE_FILE):
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # 4. [span_6](start_span)寫入檔案 (保留所有頻道，包含「其他」分類)[span_6](end_span)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        
        # A. 優先寫入 YouTube
        for entry in youtube_content:
            f.write(entry + "\n")
            
        # [span_7](start_span)B. 依據 PREFERRED_ORDER 寫入[span_7](end_span)
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for item in groups[cat]:
                f.write(item + "\n")
        
        # C. 完全保留沒被分類到的頻道（確保國際源不消失）
        for item in groups["其他"]:
            f.write(item + "\n")

    print(f"✅ 更新完成！國際源內容已全數保留，央視/4K 排序已優化。")

if __name__ == "__main__":
    run()
