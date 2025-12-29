import requests
import re

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    # 您要求的嚴格排序順序
    PREFERRED_ORDER = ["財經新聞", "新聞", "綜合", "戲劇、電影", "電影", "戲劇", "兒童", "其他"]
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        lines = r.text.splitlines()

        # 初始化分類容器
        groups = {name: [] for name in PREFERRED_ORDER}
        header = "#EXTM3U"

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                # 取得下一行 URL
                url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
                # 提取 group-title 分類
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                detected_group = group_match.group(1) if group_match else "其他"
                
                # 比對是否在您的排序名單中
                found_key = "其他"
                for order_name in PREFERRED_ORDER:
                    if order_name in detected_group:
                        found_key = order_name
                        break
                
                groups[found_key].append(f"{info_line}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

        # 一次性寫入存檔：嚴格按照 PREFERRED_ORDER 順序
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            for category in PREFERRED_ORDER:
                for entry in groups[category]:
                    f.write(entry + "\n")
                    
        print(f"成功：已按順序分類並存檔。")

    except Exception as e:
        print(f"執行出錯: {e}")

if __name__ == "__main__":
    run()

