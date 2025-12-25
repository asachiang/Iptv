import requests
import re

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    # 您指定的排序順序
    PREFERRED_ORDER = ["台灣新闻", "财经新聞", "綜合", "體育", "電影", "戲劇", "兒童", "其他"]
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        # 確保編碼正確
        r.encoding = 'utf-8'
        lines = r.text.splitlines()

        # 分類容器
        groups = {name: [] for name in PREFERRED_ORDER}
        current_header = "#EXTM3U"

        # 解析 M3U
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith("#EXTINF"):
                # 獲取標籤行
                info_line = line
                # 獲取下一行（通常是 URL）
                url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
                # 提取 group-title
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                group_name = group_match.group(1) if group_match else "其他"
                
                # 判斷屬於哪個分類，不在名單內的歸類到「其他」
                target_key = group_name if group_name in groups else "其他"
                groups[target_key].append(f"{info_line}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"):
                    current_header = line
                i += 1

        # 依照順序寫入檔案
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(current_header + "\n")
            for category in PREFERRED_ORDER:
                for entry in groups[category]:
                    f.write(entry + "\n")
                    
        print("整理完成：已按指定順序存檔。")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run()

