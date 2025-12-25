import requests
import re

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    # 定義您要求的排序順序
    PREFERRED_GROUP_ORDER = ["台灣", "新聞", "綜合", "體育", "電影", "戲劇", "兒童", "其他"]
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        content = r.text
        
        # 建立分類容器
        groups = {name: [] for name in PREFERRED_GROUP_ORDER}
        
        # 使用正則表達式切分每一個頻道區塊 (以 #EXTINF 開頭)
        # 這裡會保留 #EXTM3U 標頭以外的所有頻道資訊
        blocks = re.split(r'(?=#EXTINF)', content)
        header = "#EXTM3U\n"
        
        for block in blocks:
            block = block.strip()
            if not block or block.startswith('#EXTM3U'):
                continue
            
            # 提取分類名稱：先找 group-title，再找 #EXTGRP
            group_name = "其他"
            group_match = re.search(r'group-title="([^"]+)"', block)
            if group_match:
                group_name = group_match.group(1)
            else:
                extgrp_match = re.search(r'#EXTGRP:(.+)', block)
                if extgrp_match:
                    group_name = extgrp_match.group(1).strip()
            
            # 如果分類不在清單中，統一歸類到「其他」
            target_key = group_name if group_name in groups else "其他"
            groups[target_key].append(block)

        # 依照指定順序寫回檔案
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header)
            for group in PREFERRED_GROUP_ORDER:
                for channel_data in groups[group]:
                    f.write(channel_data + "\n")
                    
        print("成功：IPTV 列表已按指定分類排序完成。")
        
    except Exception as e:
        print(f"執行出錯: {e}")

if __name__ == "__main__":
    run()
            url = lines[i + 1] if i + 1 < len(lines) else ""
            channels.append((info, url))
            i += 2
        else:
            i += 1
    return channels

def match(info, keywords):
    return any(k in info for k in keywords)

def sort_channels(channels):
    news, finance, general, other = [], [], [], []

    for ch in channels:
        info = ch[0]
        if match(info, NEWS):
            news.append(ch)
        elif match(info, FINANCE):
            finance.append(ch)
        elif match(info, GENERAL):
            general.append(ch)
        else:
            other.append(ch)

    return news + finance + general + other

def save_m3u(channels):
    with open(SORTED_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for info, url in channels:
            f.write(info + "\n")
            f.write(url + "\n")

def run():
    try:
        # 1️⃣ 下載最新 m3u（你原本的功能）
        lines = download_m3u()

        # 2️⃣ 解析頻道
        channels = parse_channels(lines)

        # 3️⃣ 依分類排序
        sorted_channels = sort_channels(channels)

        # 4️⃣ 輸出新檔
        save_m3u(sorted_channels)

    except Exception as e:
        print("Update failed:", e)

if __name__ == "__main__":
    run()
