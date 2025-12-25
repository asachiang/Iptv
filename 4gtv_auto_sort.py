import requests
import re

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    order = ["台灣", "新聞", "綜合", "體育", "電影", "戲劇", "兒童", "其他"]
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        content = r.text
        
        # 將頻道解析成 (group_name, channel_block) 的格式
        channels = []
        blocks = re.split(r'(?=#EXTINF)', content)
        header = blocks[0] if not blocks[0].startswith('#EXTINF') else "#EXTM3U\n"
        
        groups = {name: [] for name in order}
        
        for block in blocks:
            if not block.strip() or block.startswith('#EXTM3U'):
                continue
            
            # 嘗試從 group-title="..." 或 #EXTGRP: 提取分類
            group_match = re.search(r'group-title="([^"]+)"', block)
            if not group_match:
                group_match = re.search(r'#EXTGRP:(.+)', block)
            
            group_name = group_match.group(1) if group_match else "其他"
            
            # 匹配到預設排序中，若無則歸類為「其他」
            target_group = group_name if group_name in groups else "其他"
            groups[target_group].append(block.strip())

        # 按順序組合內容
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header.strip() + "\n")
            for name in order:
                for channel in groups[name]:
                    f.write(channel + "\n")
                    
        print("IPTV 列表已更新並按順序分類。")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run()
        else:
            i += 1
    return channels

def classify(info):
    for k in NEWS:
        if k in info:
            return "news"
    for k in FINANCE:
        if k in info:
            return "finance"
    for k in GENERAL:
        if k in info:
            return "general"
    return "other"

def sort_channels(channels):
    buckets = {
        "news": [],
        "finance": [],
        "general": [],
        "other": []
    }

    for ch in channels:
        category = classify(ch[0])
        buckets[category].append(ch)

    return (
        buckets["news"]
        + buckets["finance"]
        + buckets["general"]
        + buckets["other"]
    )

def save_m3u(channels, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in channels:
            f.write(info + "\n")
            f.write(url + "\n")

def run():
    try:
        print("Downloading m3u...")
        lines = download_m3u(SOURCE_URL)

        print("Parsing channels...")
        channels = parse_channels(lines)

        print("Sorting channels...")
        sorted_channels = sort_channels(channels)

        print("Saving:", OUTPUT_FILE)
        save_m3u(sorted_channels, OUTPUT_FILE)

        print("Done!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    run()
