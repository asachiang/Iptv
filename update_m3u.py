import requests
import re

# 定義來源
SOURCES = [
    "https://raw.githubusercontent.com/asachiang/iptv/main/youtube.m3u", # 假設這是您的原始路徑
    "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
]

# 定義目標順序 (依照 group-title)
TARGET_ORDER = [
    "youtube 新聞",
    "Litv立視",
    "亞太GT",
    "體育兢技",
    "兒童卡通"
]

def main():
    all_channels = {name: [] for name in TARGET_ORDER}
    
    for url in SOURCES:
        try:
            response = requests.get(url)
            content = response.text
            
            # 使用正則表達式解析 M3U 單元
            # 匹配 #EXTINF 到下一個連結之間的內容
            pattern = re.compile(r'(#EXTINF:.*?group-title="([^"]+)".*?)\n(http.*)', re.MULTILINE)
            matches = pattern.findall(content)
            
            for full_info, group, link in matches:
                if group in TARGET_ORDER:
                    all_channels[group].append(f"{full_info}\n{link}")
        except Exception as e:
            print(f"無法讀取來源 {url}: {e}")

    # 合併結果
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group in TARGET_ORDER:
            if all_channels[group]:
                f.write("\n".join(all_channels[group]) + "\n")

    print("播放列表已更新！")

if __name__ == "__main__":
    main()
