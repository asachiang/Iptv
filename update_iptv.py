import requests
import re
import os

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    # 本地 YouTube/GPT 檔案名稱
    youtube_file = "youtube 新聞.m3u"
    # 定義 4GTV 的排序順序
    PREFERRED_ORDER = ["財經新聞", "新聞", "綜合", "戲劇、電影", "電影", "戲劇", "兒童", "其他"]
    
    try:
        # 1. 抓取網路 4GTV 列表並分類
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        lines = r.text.splitlines()

        groups = {name: [] for name in PREFERRED_ORDER}
        header = "#EXTM3U"

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info_line = line
                url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                detected_group = group_match.group(1) if group_match else "其他"
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

        # 2. 讀取本地檔案，並將「GPT-泰國」與其他內容分開
        gpt_thai_content = []
        other_youtube_content = []
        
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                content = yf.read()
                # 使用正則表達式拆分每一個頻道項目
                entries = re.findall(r'(#EXTINF:.*?\nhttp.*)', content, re.MULTILINE)
                for entry in entries:
                    if "GPT-泰國" in entry:
                        gpt_thai_content.append(entry)
                    else:
                        other_youtube_content.append(entry)
        else:
            print(f"警告：找不到 {youtube_file}")

        # 3. 按順序組合並寫入 4gtv.m3u
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            
            # 位置 1: 財經新聞
            for entry in groups["財經新聞"]: f.write(entry + "\n")
            # 位置 2: 新聞
            for entry in groups["新聞"]: f.write(entry + "\n")
            # 位置 3: 綜合
            for entry in groups["綜合"]: f.write(entry + "\n")
            
            # 位置 4: [插入點] 寫入 GPT-泰國
            for entry in gpt_thai_content:
                f.write(entry + "\n")
            
            # 位置 5 之後: 寫入剩餘的 4GTV 分類與其他 YouTube 頻道
            remaining_categories = ["戲劇、電影", "電影", "戲劇", "兒童", "其他"]
            for cat in remaining_categories:
                for entry in groups[cat]: f.write(entry + "\n")
            
            for entry in other_youtube_content:
                f.write(entry + "\n")
                    
        print(f"成功：已將『GPT-泰國』移動至第四個分類位置。")

    except Exception as e:
        print(f"執行出錯: {e}")

if __name__ == "__main__":
    run()

