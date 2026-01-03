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

def get_thailand_url(index_url):
    """
    從索引文件中提取泰國 M3U 的 URL
    iptv-org 的索引通常是直接列出各國的 .m3u 連結
    """
    lines = fetch_m3u(index_url)
    for line in lines:
        # 尋找包含 thailand.m3u 的網址行
        if "thailand.m3u" in line.lower() and line.startswith("http"):
            return line.strip()
    # 如果上面沒找到，嘗試在 #EXTINF 標籤中尋找
    for i, line in enumerate(lines):
        if "thailand" in line.lower() and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line.startswith("http"):
                return next_line
    return "https://iptv-org.github.io/iptv/countries/th.m3u" # 備用直接連結

def run():
    # 1. 定義與獲取來源
    index_url = "https://iptv-org.github.io/iptv/index.country.m3u"
    thai_url = get_thailand_url(index_url)
    
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    if thai_url:
        sources.append({"name": "Thailand", "url": thai_url})
        print(f"📍 成功鎖定泰國源網址: {thai_url}")

    youtube_file = "youtube 新聞.m3u"
    output_file = "4gtv.m3u"
    
    # 2. 定義要求的排序
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞",
        "新聞財經",
        "綜合",
        "Thailand",
        "歷年春晚",
        "戲劇、電影與紀錄片",
        "兒童與青少年",
        "音樂綜藝",
        "運動健康生活",
        "衛視IPV4"
    ]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    groups["其他"] = []
    header = "#EXTM3U"

    # --- 步驟 A: 處理所有來源 ---
    for src in sources:
        print(f"📡 正在處理: {src['name']}")
        lines = fetch_m3u(src['url'])
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                content_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].startswith("#EXTINF"):
                    if lines[j].strip():
                        content_lines.append(lines[j].strip())
                    j += 1
                
                full_content = "\n".join(content_lines)
                chan_name = info_line.split(',')[-1].upper()
                
                # 判定分類
                target_key = "其他"
                
                # 強制歸類：如果是從泰國源抓下來的，直接進 Thailand 群組
                if src['name'] == "Thailand":
                    target_key = "Thailand"
                else:
                    search_text = chan_name + info_line.upper()
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

                # 統一修改 group-title 標籤
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

    # --- 步驟 B: 處理 YouTube ---
    youtube_content = []
    if os.path.exists(youtube_file):
        with open(youtube_file, "r", encoding="utf-8") as yf:
            youtube_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

    # --- 步驟 C: 寫入檔案 ---
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        
        # 1. YouTube 優先
        for entry in youtube_content:
            f.write(entry + "\n")
            
        # 2. 依照順序寫入各分類
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            if groups[cat]:
                print(f"📦 寫入分類: {cat} ({len(groups[cat])} 個頻道)")
                for item in groups[cat]:
                    f.write(item + "\n")
        
        # 3. 其他分類
        for item in groups["其他"]:
            f.write(item + "\n")

    print(f"✅ 更新完成！最終檔案：{output_file}")

if __name__ == "__main__":
    run()
