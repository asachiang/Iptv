import requests
import re

# 1. 定義來源
SOURCE_YOUTUBE = "https://raw.githubusercontent.com/asachiang/iptv/main/youtube%E6%96%B0%E8%81%9E.m3u"
SOURCE_4GTV = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"

# 2. 定義目標分類順序
TARGET_ORDER = ["youtube 新聞", "Litv立視", "亞太GT", "體育兢技", "兒童卡通"]

# 3. 4GTV 的匹配規則
CATEGORY_MAP_4GTV = {
    "Litv立視": ["litv", "立視"],
    "亞太GT": ["亞太", "gt"],
    "體育兢技": ["體育", "兢技", "運動", "sports"],
    "兒童卡通": ["兒童", "卡通", "kids", "anime"]
}

def main():
    results = {cat: [] for cat in TARGET_ORDER}
    
    # --- 處理 YouTube 新聞 (全部強行歸類) ---
    try:
        print(f"正在抓取 YouTube 新聞: {SOURCE_YOUTUBE}")
        res = requests.get(SOURCE_YOUTUBE, timeout=15)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            # 匹配 #EXTINF 到下一個連結
            items = re.findall(r'(#EXTINF:.*?\nhttp.*)', res.text)
            for item in items:
                # 強制修改或添加 group-title 為 "youtube 新聞"
                clean_item = re.sub(r'group-title="[^"]+"', 'group-title="youtube 新聞"', item)
                if 'group-title="' not in clean_item:
                    clean_item = clean_item.replace('#EXTINF:', '#EXTINF:-1 group-title="youtube 新聞",')
                results["youtube 新聞"].append(clean_item)
            print(f"✅ YouTube 新聞：共抓取 {len(results['youtube 新聞'])} 個頻道")
    except Exception as e:
        print(f"讀取 YouTube 來源失敗: {e}")

    # --- 處理 4GTV 來源 ---
    try:
        print(f"正在抓取 4GTV 來源: {SOURCE_4GTV}")
        res = requests.get(SOURCE_4GTV, timeout=15)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            items = re.findall(r'(#EXTINF:.*?\nhttp.*)', res.text)
            for item in items:
                group_match = re.search(r'group-title="([^"]+)"', item, re.IGNORECASE)
                group_name = group_match.group(1).lower() if group_match else ""
                
                for label, keywords in CATEGORY_MAP_4GTV.items():
                    if any(k.lower() in group_name for k in keywords):
                        results[label].append(item)
                        break
    except Exception as e:
        print(f"讀取 4GTV 來源失敗: {e}")

    # --- 寫入檔案 ---
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for label in TARGET_ORDER:
            if results[label]:
                for channel in results[label]:
                    f.write(f"\n{channel.strip()}\n")
    
    print("\n✅ 檔案已更新，分類順序正確。")

if __name__ == "__main__":
    main()
