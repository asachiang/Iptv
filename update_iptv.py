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
    """從索引文件中精確提取泰國 M3U 連結"""
    lines = fetch_m3u(index_url)
    for line in lines:
        if "thailand.m3u" in line.lower() and line.startswith("http"):
            return line.strip()
    return "https://iptv-org.github.io/iptv/countries/th.m3u"

def run():
    # 1. 來源定義
    index_url = "https://iptv-org.github.io/iptv/index.country.m3u"
    thai_url = get_thailand_url(index_url)
    
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    youtube_file = "youtube 新聞.m3u"
    main_output = "4gtv.m3u"
    thai_output = "Thailand.m3u" # 獨立儲存的泰國列表
    
    # 2. 排序定義
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞", "新聞財經", "綜合", "Thailand", 
        "歷年春晚", "戲劇、電影與紀錄片", "兒童與青少年", 
        "音樂綜藝", "運動健康生活", "其它"
    ]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    header = "#EXTM3U"
    thailand_channels = [] # 存放提取出的泰國頻道

    # --- 步驟 A: 專門處理泰國源 ---
    print(f"📡 擷取泰國直播源: {thai_url}")
    thai_lines = fetch_m3u(thai_url)
    i = 0
    while i < len(thai_lines):
        line = thai_lines[i].strip()
        if line.startswith("#EXTINF"):
            info = line
            # 取得網址
            content = ""
            if i + 1 < len(thai_lines):
                content = thai_lines[i+1].strip()
            
            # 強制標註為 Thailand 分類
            if 'group-title="' in info:
                info = re.sub(r'group-title="[^"]+"', 'group-title="Thailand"', info)
            else:
                info = info.replace("#EXTINF:-1", '#EXTINF:-1 group-title="Thailand"')
            
            channel_entry = f"{info}\n{content}"
            thailand_channels.append(channel_entry)
            groups["Thailand"].append(channel_entry)
            i += 2
        else: i += 1

    # --- 步驟 B: 處理其他網路來源 ---
    for src in sources:
        print(f"📡 處理來源: {src['name']}")
        lines = fetch_m3u(src['url'])
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                content = lines[i+1].strip() if i+1 < len(lines) else ""
                chan_name = info_line.split(',')[-1].upper()
                
                # 分類邏輯
                target_key = "其它"
                search_text = chan_name + info_line.upper()
                
                if any(k in search_text for k in ["新聞", "NEWS", "財經"]): target_key = "新聞財經"
                elif any(k in search_text for k in ["綜合", "GENERAL", "4GTV"]): target_key = "綜合"
                elif "春晚" in search_text: target_key = "歷年春晚"
                elif any(k in search_text for k in ["電影", "戲劇", "MOVIE", "DRAMA"]): target_key = "戲劇、電影與紀錄片"
                elif any(k in search_text for k in ["兒童", "KIDS", "CARTOON"]): target_key = "兒童與青少年"
                elif any(k in search_text for k in ["音樂", "綜藝", "MUSIC", "VARIETY"]): target_key = "音樂綜藝"
                elif any(k in search_text for k in ["運動", "SPORTS", "健康"]): target_key = "運動健康生活"

                # 更新標籤並存入群組
                info_line = re.sub(r'group-title="[^"]+"', f'group-title="{target_key}"', info_line) if 'group-title="' in info_line else info_line.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_key}"')
                groups[target_key].append(f"{info_line}\n{content}")
                i += 2
            else: i += 1

    # --- 步驟 C: 寫入檔案 ---
    # 1. 獨立儲存 Thailand.m3u
    with open(thai_output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(thailand_channels))
    print(f"✅ 已獨立儲存泰國頻道: {thai_output}")

    # 2. 儲存整合後的 4gtv.m3u
    with open(main_output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        # 讀取本地 YouTube
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                f.write("".join([l for l in yf if not l.startswith("#EXTM3U")]))
        # 依序寫入分類
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for item in groups[cat]:
                f.write(item + "\n")

    print(f"✅ 全部分類更新完成！")

if __name__ == "__main__":
    run()
