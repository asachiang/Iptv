import requests
import re

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    # 您要求的嚴格排序順序
    PREFERRED_ORDER = ["台灣", "新聞", "綜合", "體育", "電影", "戲劇", "兒童", "其他"]
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        lines = r.text.splitlines()

        # 準備分類容器：key 是分類名稱，value 是該分類的所有頻道清單
        groups = {name: [] for name in PREFERRED_ORDER}
        header = "#EXTM3U"

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
                # 提取分類：從 group-title="..." 提取
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                detected_group = group_match.group(1) if group_match else "其他"
                
                # 檢查偵測到的分類是否在您的清單中 (關鍵字匹配)
                found = False
                for order_name in PREFERRED_ORDER:
                    if order_name in detected_group:
                        groups[order_name].append(f"{info_line}\n{url_line}")
                        found = True
                        break
                
                if not found:
                    groups["其他"].append(f"{info_line}\n{url_line}")
                
                i += 2
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

        # 一次性回寫存檔：嚴格按照 PREFERRED_ORDER 的順序
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            for category in PREFERRED_ORDER:
                if groups[category]: # 只有當該分類有頻道時才寫入
                    for entry in groups[category]:
                        f.write(entry + "\n")
                    
        print(f"排序存檔完成！已處理 {sum(len(v) for v in groups.values())} 個頻道。")

    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    run()
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

