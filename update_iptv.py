import requests
import re
import os
import concurrent.futures

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

def check_url(url):
    """嚴格篩選：檢查網址是否可播放"""
    try:
        # 使用 HEAD 請求節省流量，僅檢查狀態碼
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code in [200, 302]
    except:
        return False

def get_thailand_url(index_url):
    """獲取泰國源連結"""
    lines = fetch_m3u(index_url)
    for line in lines:
        if "thailand.m3u" in line.lower() and line.startswith("http"):
            return line.strip()
    return "https://iptv-org.github.io/iptv/countries/th.m3u"

def run():
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
    
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞", "新聞財經", "綜合", "Thailand", 
        "衛视IPV4", "央視IPV4", "4K8K頻道",
        "戲劇、電影與紀錄片", "兒童與青少年", 
        "音樂綜藝", "運動健康生活", "其它"
    ]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    thailand_only_list = [] 

    # --- 步驟 A: 處理泰國源 + 效驗 ---
    print(f"📡 正在篩選泰國頻道 (此步驟較慢): {thai_url}")
    thai_lines = fetch_m3u(thai_url)
    
    # 提取頻道資訊對
    temp_thai = []
    for i in range(len(thai_lines)):
        if thai_lines[i].startswith("#EXTINF"):
            info = thai_lines[i]
            url = thai_lines[i+1].strip() if i+1 < len(thai_lines) else ""
            if url: temp_thai.append((info, url))

    # 使用多執行緒加速效驗
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda p: check_url(p[1]), temp_thai))
    
    for (info, url), is_valid in zip(temp_thai, results):
        if is_valid:
            info = re.sub(r'group-title="[^"]+"', 'group-title="Thailand"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", '#EXTINF:-1 group-title="Thailand"')
            entry = f"{info}\n{url}"
            groups["Thailand"].append(entry)
            thailand_only_list.append(entry)

    # --- 步驟 B: 處理其餘來源 (不逐一效驗以維持速度，或視需求加入) ---
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

                info = re.sub(r'group-title="[^"]+"', f'group-title="{target}"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target}"')
                groups[target].append(f"{info}\n{url}")
                i += 2
            else: i += 1

    # --- 步驟 C: 寫入檔案 ---
    with open(thai_output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(thailand_only_list))

    with open(main_output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                f.write("".join([line for line in yf if not line.startswith("#EXTM3U")]))

        for cat in PREFERRED_ORDER:
            if cat == "YOUTUBE油管新聞": continue 
            for item in groups[cat]:
                f.write(item + "\n")

    print(f"✅ 更新完成！已排除無法播放的泰國頻道。")

if __name__ == "__main__":
    run()
