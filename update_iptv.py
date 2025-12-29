import requests
import re
import os

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    # 本地 YouTube 新聞檔案名稱
    youtube_file = "youtube 新聞.m3u"
    # 您要求的嚴格排序順序
    PREFERRED_ORDER = ["財經新聞", "新聞", "綜合", "戲劇、電影", "電影", "戲劇", "兒童", "其他"]
    
    try:
        # 1. 抓取網路 4GTV 列表
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

        # 2. [span_0](start_span)讀取本地 YouTube 新聞內容[span_0](end_span)
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                y_lines = yf.readlines()
                # [span_1](start_span)排除第一行的 #EXTM3U，只取頻道資訊內容[span_1](end_span)
                for y_line in y_lines:
                    if not y_line.startswith("#EXTM3U") and y_line.strip():
                        youtube_content.append(y_line.strip())
        else:
            print(f"警告：找不到 {youtube_file}，將跳過此部分。")

        # 3. 一次性寫入存檔
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            
            # [span_2](start_span)首先寫入 YouTube 新聞內容[span_2](end_span)
            for yt_line in youtube_content:
                f.write(yt_line + "\n")
            
            # 接著按順序寫入 4GTV 分類內容
            for category in PREFERRED_ORDER:
                for entry in groups[category]:
                    f.write(entry + "\n")
                    
        print(f"成功：已將 YouTube 新聞置頂，並按順序完成 4GTV 分類存檔。")

    except Exception as e:
        print(f"執行出錯: {e}")

if __name__ == "__main__":
    run()

