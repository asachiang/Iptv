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
    thai_output = "Thailand.m3u" 
    
    # 2. 依照您的要求定義新排序
    PREFERRED_ORDER = [
        "YOUTUBE油管新聞", "新聞財經", "綜合", "Thailand", 
        "衛视IPV4", "央視IPV4", "4K8K頻道",
        "戲劇、電影與紀錄片", "兒童與青少年", 
        "音樂綜藝", "運動健康生活", "其它"
    ]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    header = "#EXTM3U"
    thailand_channels = [] 

    # --- 步驟 A: 專門處理與擷取泰國源 ---
    print(f"📡 擷取泰國直播源: {thai_url}")
    thai_lines = fetch_m3u(thai_url)
    i = 0
    while i < len(thai_lines):
        line = thai_lines[i].strip()
        if line.startswith("#EXTINF"):
            info = line
            content = thai_lines[i+1].strip() if i+1 < len(thai_lines) else ""
            
            # 強制標註為 Thailand 分類並獨立儲存
            info = re.sub(r'group-title="[^"]+"', 'group-title="Thailand"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", '#EXTINF:-1 group-title="Thailand"')
            
            entry = f"{info}\n{content}"
            thailand_channels.append(entry)
            groups["Thailand"].append(entry)
            i += 2
        else: i += 1

    # --- 步驟 B: 處理其餘網路來源 ---
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
