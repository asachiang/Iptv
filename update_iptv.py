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
    # 1. 定義來源 (整合 4GTV、香港與國際源)
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    youtube_file = "youtube 新聞.m3u"
    output_file = "4gtv.m3u"
    
    # 2. 定義要求的排序 (移除央視與 4K)
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞",
        "新聞財經",
        "綜合",
        "衛視IPV4",
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
        print(f"正在處理來源: {src['name']}")
        lines = fetch_m3u(src['url'])
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                # 抓取該頻道後續所有內容 (含多行網址或標籤)
                content_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].startswith("#EXTINF"):
                    if lines[j].strip():
                        content_lines.append(lines[j].strip())
                    j += 1
                
                full_content = "\n".join(content_lines)
                
                # 取得頻道名稱與原始分類進行判定
                chan_name = info_line.split(',')[-1].upper()
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                original_group = group_match.group(1).upper() if group_match else ""
                search_text = chan_name + original_group
                
                target_key = "其他"

                # 分類判斷
                if any(k in search_text for k in ["衛視", "卫视", "TVB", "翡翠", "鳳凰", "HK", "HONGKONG"]):
                    target_key = "衛視IPV4"
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

                # 重新修正 group-title 標籤
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

    # --- 步驟 B: 讀取本地 YouTube ---
    youtube_content = []
    if os.path.exists(youtube_file):
        with open(youtube_file, "r", encoding="utf-8") as yf:
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # --- 步驟 C: 依序寫入 (確保更新 4gtv.m3u) ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        
        # 1. YouTube
        for entry in youtube_content:
            f.write(entry + "\n")
            
        # 2. 指定分類
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for item in groups[cat]:
                f.write(item + "\n")
        
        # 3. 國際源其餘內容 (不篩選，全數保留)
        for item in groups["其他"]:
            f.write(item + "\n")

    print(f"✅ 更新完成！已產出檔案：{output_file}")

if __name__ == "__main__":
    run()
