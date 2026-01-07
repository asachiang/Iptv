import requests
import re
import urllib.parse

# 1. 來源連結 (修正中文編碼問題)
# 使用 quote 確保「youtube新聞.m3u」能被正確讀取
yt_filename = urllib.parse.quote("youtube新聞.m3u")
SOURCE_YOUTUBE = f"https://raw.githubusercontent.com/asachiang/iptv/main/{yt_filename}"
SOURCE_4GTV = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"

# 2. 目標分類順序
TARGET_ORDER = ["youtube 新聞", "Litv立視", "亞太GT", "體育兢技", "兒童卡通"]

# 3. 4GTV 匹配規則
CATEGORY_MAP_4GTV = {
    "Litv立視": ["litv", "立視"],
    "亞太GT": ["亞太", "gt"],
    "體育兢技": ["體育", "兢技", "運動", "sports"],
    "兒童卡通": ["兒童", "卡通", "kids", "anime"]
}

def main():
    results = {cat: [] for cat in TARGET_ORDER}
    
    # --- 處理 YouTube 新聞 (強制全抓) ---
    print(f"嘗試抓取 YouTube: {SOURCE_YOUTUBE}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(SOURCE_YOUTUBE, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        
        if res.status_code == 200:
            # 兼容不同換行格式，尋找 #EXTINF 到下一個連結
            content = res.text
            items = re.findall(r'(#EXTINF:.*?\nhttp.*)', content)
            
            if not items:
                # 備用方案：如果正則沒抓到，嘗試按行切割
                print("正則表達式未抓到頻道，嘗試簡易切分...")
                lines = content.split('\n')
                for i in range(len(lines)):
                    if lines[i].startswith('#EXTINF:'):
                        if i + 1 < len(lines) and lines[i+1].startswith('http'):
                            items.append(f"{lines[i]}\n{lines[i+1]}")

            for item in items:
                # 重新強制標註分類為 "youtube 新聞"
                # 先移除舊的 group-title
                temp_item = re.sub(r'group-title="[^"]+"', '', item)
                # 在 #EXTINF 之後插入新的 group-title
                clean_item = temp_item.replace('#EXTINF:', '#EXTINF:-1 group-title="youtube 新聞",')
                results["youtube 新聞"].append(clean_item)
            
            print(f"✅ YouTube 新聞成功：抓到 {len(results['youtube 新聞'])} 個頻道")
        else:
            print(f"❌ YouTube 連結無效，狀態碼: {res.status_code}")
    except Exception as e:
        print(f"❌ 抓取 YouTube 發生錯誤: {e}")

    # --- 處理 4GTV ---
    try:
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
        print(f"❌ 抓取 4GTV 錯誤: {e}")

    # --- 寫入檔案 ---
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for label in TARGET_ORDER:
            if results[label]:
                for channel in results[label]:
                    f.write(f"\n{channel.strip()}\n")
    
    print("\n[完成] 播放列表已重新生成。")

if __name__ == "__main__":
    main()
