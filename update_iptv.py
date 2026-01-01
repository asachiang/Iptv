import requests
import re
import os

def fetch_m3u(url):
    [span_0](start_span)"""抓取網路上的 M3U 檔案[span_0](end_span)"""
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
    [span_1](start_span)URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"[span_1](end_span)
    [span_2](start_span)YOUTUBE_FILE = "youtube 新聞.m3u"[span_2](end_span)
    [span_3](start_span)OUTPUT_FILE = "4gtv.m3u"[span_3](end_span)
    
    # 2. 定義要求的精確排序標籤
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
    [span_4](start_span)header = "#EXTM3U"[span_4](end_span)

    # --- 步驟 A: 處理網路來源 ---
    print(f"正在處理 4GTV 來源...")
    [span_5](start_span)lines = fetch_m3u(URL_4GTV)[span_5](end_span)
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        [span_6](start_span)if line.startswith("#EXTINF"):[span_6](end_span)
            info_line = line
            [span_7](start_span)url_line = lines[i+1].strip() if i+1 < len(lines) else ""[span_7](end_span)
            
            # 獲取原始標籤
            [span_8](start_span)match = re.search(r'group-title="([^"]+)"', info_line)[span_8](end_span)
            [span_9](start_span)detected = match.group(1) if match else "其他"[span_9](end_span)
            
            # 強制分類邏輯：根據關鍵字歸類到您的新排序中
            target_key = "其他"
            
            # 檢查關鍵字並分配到對應的 PREFERRED_ORDER
            if any(k in detected for k in ["新聞", "財經"]):
                target_key = "新聞財經"
            elif any(k in detected for k in ["綜合", "General"]):
                target_key = "綜合"
            elif any(k in detected for k in ["CCTV", "央視", "央视"]):
                target_key = "央视IPV4"
            elif "衛視" in detected or "卫视" in detected:
                target_key = "衛視IPV4"
            elif any(k in detected for k in ["4K", "8K", "超高清"]):
                target_key = "4K8K頻道"
            elif "春晚" in detected:
                target_key = "歷年春晚"
            elif any(k in detected for k in ["戲劇", "電影", "紀錄片", "Movie", "Drama"]):
                target_key = "戲劇、電影與紀錄片"
            elif any(k in detected for k in ["兒童", "少兒", "卡通", "Kids"]):
                target_key = "兒童與青少年"
            elif any(k in detected for k in ["音樂", "綜藝", "Music", "Variety"]):
                target_key = "音樂綜藝"
            elif any(k in detected for k in ["運動", "健康", "生活", "體育", "Sports"]):
                target_key = "運動健康生活"
            
            # [span_10](start_span)存入對應組別[span_10](end_span)
            if target_key in groups:
                groups[target_key].append(f"{info_line}\n{url_line}")
            else:
                groups["其他"].append(f"{info_line}\n{url_line}")
            i += 2
        else:
            [span_11](start_span)if line.startswith("#EXTM3U"): header = line[span_11](end_span)
            i += 1

    # --- 步驟 B: 處理本地 YouTube ---
    youtube_content = []
    [span_12](start_span)if os.path.exists(YOUTUBE_FILE):[span_12](end_span)
        with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
            # [span_13](start_span)讀取整行並移除潛在的標頭[span_13](end_span)
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # --- 步驟 C: 依序寫入檔案 ---
    [span_14](start_span)with open(OUTPUT_FILE, "w", encoding="utf-8") as f:[span_14](end_span)
        [span_15](start_span)f.write(header + "\n")[span_15](end_span)

        # 1. 第一順位：YOUTUBE
        for line in youtube_content:
            [span_16](start_span)f.write(line + "\n")[span_16](end_span)

        # 2. [span_17](start_span)依照 PREFERRED_ORDER 順序寫入其餘分類[span_17](end_span)
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            [span_18](start_span)for entry in groups[cat]:[span_18](end_span)
                # 確保寫入時 group-title 被更新為您的分類名稱，這樣電視 App 才會顯示正確分類
                updated_entry = re.sub(r'group-title="[^"]+"', f'group-title="{cat}"', entry)
                f.write(updated_entry + "\n")

        # 3. 最後寫入未分類
        for entry in groups["其他"]:
            f.write(entry + "\n")

    print(f"✅ 排序更新完成！已儲存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
