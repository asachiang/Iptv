import requests
import re
import os
import concurrent.futures

# ========= 基本設定 =========
INDEX_URL = "https://iptv-org.github.io/iptv/index.country.m3u"
OUTPUT_MAIN = "4gtv.m3u"
OUTPUT_THAI = "Thailand.m3u"
YOUTUBE_FILE = "youtube 新聞.m3u"

TIMEOUT = 5   # 嚴格篩選：連線超過 5 秒即捨棄
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ========= 嚴格定義分類順序 =========
CATEGORY_ORDER = [
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

# ========= 工具函式 =========
def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text.splitlines()
    except:
        return []

def stream_alive(url):
    """檢測直播源是否可用 (嚴格篩選)"""
    try:
        # 使用 stream=True 並只讀取開頭，避免下載整個檔案
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

def get_thailand_url():
    lines = fetch_m3u(INDEX_URL)
    for l in lines:
        if "thailand.m3u" in l.lower() and l.startswith("http"):
            return l.strip()
    return "https://iptv-org.github.io/iptv/countries/th.m3u"

def run():
    groups = {k: [] for k in CATEGORY_ORDER}
    thailand_only = []

    # 1. 處理泰國源 (包含嚴格效驗)
    thai_url = get_thailand_url()
    print(f"📡 擷取泰國源並進行嚴格篩選: {thai_url}")
    thai_lines = fetch_m3u(thai_url)
    
    thai_tasks = []
    for i in range(len(thai_lines)):
        if thai_lines[i].startswith("#EXTINF"):
            info = thai_lines[i]
            url = thai_lines[i+1].strip() if i+1 < len(thai_lines) else ""
            if url: thai_tasks.append((info, url))

    # 使用多執行緒加速檢測，否則會跑很久
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(lambda p: stream_alive(p[1]), thai_tasks))

    for (info, url), is_alive in zip(thai_tasks, results):
        if is_alive:
            # 強制歸類
            new_info = re.sub(r'group-title="[^"]+"', 'group-title="Thailand"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", '#EXTINF:-1 group-title="Thailand"')
            entry = f"{new_info}\n{url}"
            groups["Thailand"].append(entry)
            thailand_only.append(entry)

    # 2. 處理其他來源 (範例：4GTV, 香港等)
    other_sources = [
        "https://jody.im5k.fun/4gtv.m3u",
        "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"
    ]
    
    for src in other_sources:
        print(f"📡 處理來源: {src}")
        lines = fetch_m3u(src)
        i = 0
        while i < len(lines):
            if lines[i].startswith("#EXTINF"):
                info = lines[i]
                url = lines[i+1].strip() if i+1 < len(lines) else ""
                name = info.split(',')[-1].upper()
                
                # 自動分類邏輯
                target = "其它"
                if any(k in name or k in info.upper() for k in ["新聞", "NEWS", "財經"]): target = "新聞財經"
                elif any(k in name or k in info.upper() for k in ["綜合", "GENERAL", "4GTV"]): target = "綜合"
                elif any(k in name or k in info.upper() for k in ["衛視", "卫视", "TVB", "翡翠", "鳳凰", "HK"]): target = "衛视IPV4"
                elif "CCTV" in name or "央視" in name: target = "央視IPV4"
                elif any(k in name for k in ["4K", "8K"]): target = "4K8K頻道"
                elif any(k in name for k in ["電影", "戲劇", "MOVIE", "DRAMA"]): target = "戲劇、電影與紀錄片"
                elif any(k in name for k in ["兒童", "KIDS", "少兒"]): target = "兒童與青少年"
                elif any(k in name for k in ["音樂", "綜藝", "MUSIC", "VARIETY"]): target = "音樂綜藝"
                elif any(k in name for k in ["運動", "SPORTS", "體育"]): target = "運動健康生活"

                new_info = re.sub(r'group-title="[^"]+"', f'group-title="{target}"', info) if 'group-title="' in info else info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target}"')
                groups[target].append(f"{new_info}\n{url}")
                i += 2
            else:
                i += 1

    # 3. 寫入獨立 Thailand.m3u
    with open(OUTPUT_THAI, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(thailand_only))

    # 4. 寫入主列表 4gtv.m3u
    with open(OUTPUT_MAIN, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        # A. YouTube 優先 (從本地讀取)
        if os.path.exists(YOUTUBE_FILE):
            with open(YOUTUBE_FILE, "r", encoding="utf-8") as yf:
                f.write("".join([l for l in yf if not l.startswith("#EXTM3U")]))
        
        # B. 依順序寫入各群組
        for cat in CATEGORY_ORDER:
            if cat == "YOUTUBE油管新聞": continue
            for channel in groups[cat]:
                f.write(channel + "\n")

    print(f"🚀 執行完畢！已產出 {OUTPUT_MAIN} 與 {OUTPUT_THAI}")

if __name__ == "__main__":
    run()
