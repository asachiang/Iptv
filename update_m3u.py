import requests
import re

# 1. 來源連結
# 修正了 youtube.m3u 的抓取路徑，確保能抓到原始資料
SOURCES = [
    "https://raw.githubusercontent.com/asachiang/iptv/main/youtube新聞.m3u",
    "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
]

# 2. 關鍵字匹配地圖 (模糊匹配，只要包含關鍵字就歸類)
CATEGORY_MAP = {
    "YOUTUBE油管新聞": ["youtube", "油管新聞", "新聞"],
    "Litv立視": ["litv", "立視"],
    "亞太GT": ["亞太", "gt", "亞太gt"],
    "體育兢技": ["體育", "兢技", "運動", "sports", "體育競技"],
    "兒童卡通": ["兒童", "卡通", "kids", "anime", "幼兒", "動漫"]
}

def main():
    # 初始化儲存容器
    results = {cat: [] for cat in CATEGORY_MAP.keys()}
    
    for url in SOURCES:
        try:
            print(f"正在抓取來源: {url}")
            # 加入 headers 模擬瀏覽器，避免被部分服務阻擋
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"跳過：網址回應錯誤 {response.status_code}")
                continue

            content = response.text
            
            # 使用更強大的正規表達式匹配 M3U 區塊
            # 匹配 #EXTINF 開始到下一個 http 連結結束
            items = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content)
            
            for item in items:
                # 取得 group-title 的內容進行分類判斷
                group_match = re.search(r'group-title="([^"]+)"', item, re.IGNORECASE)
                group_name = group_match.group(1) if group_match else ""
                
                # 同時也檢查頻道名稱，增加匹配成功率
                title_match = re.search(r',(.+)$', item.split('\n')[0])
                display_name = title_match.group(1) if title_match else ""
                
                search_text = (group_name + display_name).lower()

                # 依序歸類
                for final_label, keywords in CATEGORY_MAP.items():
                    if any(k.lower() in search_text for k in keywords):
                        # 統一修改 group-title 讓輸出整齊美觀
                        clean_item = re.sub(r'group-title="[^"]+"', f'group-title="{final_label}"', item)
                        results[final_label].append(clean_item)
                        break

        except Exception as e:
            print(f"讀取錯誤 {url}: {e}")

    # 3. 輸出合併後的檔案
    count = 0
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for label in CATEGORY_MAP.keys():
            if results[label]:
                print(f"✅ 分類 [{label}]：找到 {len(results[label])} 個頻道")
                for channel_data in results[label]:
                    f.write(f"\n{channel_data.strip()}\n")
                    count += 1
            else:
                print(f"❌ 分類 [{label}]：未找到符合的頻道")

    print(f"\n處理完成！總計共 {count} 個頻道已寫入 playlist.m3u")

if __name__ == "__main__":
    main()
