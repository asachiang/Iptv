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
    """從索引中提取泰國 M3U 連結"""
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
    thai_output = "Thailand.m3u" 
    
    # 2. 嚴格定義排序清單
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞", 
        "新聞財經", 
        "綜合", 
        "Thailand", 
        "衛视IPV4", 
        "央視IPV4", 
        "4K8K頻道",
        "戲劇、電影與紀錄片", 
        "兒童與青少年", 
        "音樂綜藝", 
        "運動健康生活", 
        "其它"
    ]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    thailand_only_list = [] 

    # --- 步驟 A: 處理泰國專屬源 (優先處理並強制鎖定) ---
    print(f"📡 正在擷取泰國頻道: {thai_url}")
    thai_lines = fetch_m3u(thai_url)
    i = 0
    while i < len(thai_lines):
        line = thai_lines[i].strip()
        if line.startswith("#EXTINF"):
            info = line
            url = thai_lines[i+1].strip() if i+1 < len(thai_lines) else ""
            # 強制分類標籤為 Thailand
            info = re.sub(r'group-title="[^"]+"', 'group-title="Thailand"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", '#EXTINF:-1 group-title="Thailand"')
            entry = f"{info}\n{url}"
            groups["Thailand"].append(entry)
            thailand_only_list.append(entry)
            i += 2
        else: i += 1

    # --- 步驟 B: 處理其他來源 ---
    for src in sources:
        print(f"📡 處理來源: {src['name']}")
        lines = fetch_m3u(src['url'])
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url = lines[i+1].strip() if i+1 < len(lines) else ""
                name = info.split(',')[-1].upper()
                search_text = (name + info.upper())
                
                # 嚴格分類邏輯 (關鍵字排序影響結果)
                target = "其它"
                if any(k in search_text for k in ["CCTV", "央視", "中央台"]): target = "央視IPV4"
                elif any(k in search_text for k in ["衛視", "卫视", "TVB", "翡翠", "鳳凰", "HK", "HONG KONG"]): target = "衛视IPV4"
                elif any(k in search_text for k in ["4K", "8K", "ULTRAHD", "UHD"]): target = "4K8K頻道"
                elif any(k in search_text for k in ["新聞", "NEWS", "財經", "股市"]): target = "新聞財經"
                elif any(k in search_text for k in ["綜合", "GENERAL", "4GTV"]): target = "綜合"
                elif any(k in search_text for k in ["電影", "戲劇", "MOVIE", "DRAMA", "影視"]): target = "戲劇、電影與紀錄片"
                elif any(k in search_text for k in ["兒童", "KIDS", "CARTOON", "少兒"]): target = "兒童與青少年"
                elif any(k in search_text for k in ["音樂", "綜藝", "MUSIC", "VARIETY"]): target = "音樂綜藝"
                elif any(k in search_text for k in ["運動", "SPORTS", "健康", "體育"]): target = "運動健康生活"

                # 更新標籤
                info = re.sub(r'group-title="[^"]+"', f'group-title="{target}"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target}"')
                groups[target].append(f"{info}\n{url}")
                i += 2
            else: i += 1

    # --- 步驟 C: 依序寫入檔案 ---
    # 1. 寫入獨立的 Thailand.m3u
    with open(thai_output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(thailand_only_list))

    # 2. 寫入主列表 4gtv.m3u
    with open(main_output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        # 讀取 YouTube
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                f.write("".join([line for line in yf if not line.startswith("#EXTM3U")]))

        # 按照 PREFERRED_ORDER 順序強制寫入
        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue # 已經先寫入過了
            if groups[cat]:
                print(f"✅ 寫入分類: {cat} ({len(groups[cat])} 頻道)")
                for item in groups[cat]:
                    f.write(item + "\n")

    print(f"🚀 更新完成！Thailand.m3u 與 4gtv.m3u 已就緒。")

if __name__ == "__main__":
    run()
