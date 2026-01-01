import requests
import re

def fetch_m3u(url):
    """抓取 M3U 來源"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text.splitlines()
    except Exception as e:
        print(f"❌ 抓取失敗 {url}: {e}")
        return []

def run():
    # ===== 1. 定義來源 =====
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/apt/master/m3u/iptv-select.m3u"}
    ]

    all_channels = ["#EXTM3U"]
    seen_urls = set()

    # ===== 2. 抓取並合併資料 =====
    for s in sources:
        print(f"正在處理: {s['name']}")
        lines = fetch_m3u(s['url'])
        
        current_info = ""
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                current_info = line
            elif line.startswith("http") and current_info:
                if line not in seen_urls:
                    all_channels.append(current_info)
                    all_channels.append(line)
                    seen_urls.add(line)
                current_info = ""

    # ===== 3. 儲存成檔案 =====
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(all_channels))
    print(f"✅ 更新完成，共收集 {len(seen_urls)} 個頻道，已存至 live.m3u")

# 確保 GitHub Action 執行時會跑 run()
if __name__ == "__main__":
    run()
