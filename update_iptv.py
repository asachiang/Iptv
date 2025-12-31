import requests
import re
import os

def run():
    # 定義多個來源網址
    urls = [
        "https://jody.im5k.fun/4gtv.m3u",
        "https://jody.im5k.fun/smart.m3u"  # 新加入的來源
    ]
    
    youtube_file = "youtube 新聞.m3u"
    PREFERRED_ORDER = ["財經新聞", "新聞", "綜合", "泰国、新聞", "電影", "戲劇", "兒童", "其他"]
    
    # 初始化分類容器
    groups = {name: [] for name in PREFERRED_ORDER}
    header = "#EXTM3U"

    try:
        # 1. 循環抓取所有網路 M3U 列表
        for url in urls:
            print(f"正在抓取: {url}...")
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                r.encoding = 'utf-8'
                lines = r.text.splitlines()

                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith("#EXTINF"):
                        info_line = line
                        url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                        
                        # 提取分類標籤
                        group_match = re.search(r'group-title="([^"]+)"', info_line)
                        detected_group = group_match.group(1) if group_match else "其他"
                        
                        # 比對優先排序順序
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
            except Exception as url_e:
                print(f"抓取 {url} 失敗: {url_e}")

        # 2. 讀取本地 YouTube 新聞內容
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                y_lines = yf.readlines()
                # 排除第一行標頭，只取頻道內容
                for y_line in y_lines:
                    if not y_line.startswith("#EXTM3U") and y_line.strip():
                        youtube_content.append(y_line.strip())
        else:
            print(f"警告：找不到 {youtube_file}，將跳過此部分。")

        # 3. 寫入最終檔案
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            
            # 首先寫入置頂的 YouTube 內容
            for yt_line in youtube_content:
                f.write(yt_line + "\n")
            
            # 接著按自定義順序寫入合併後的 4GTV 與 Smart 分類內容
            for category in PREFERRED_ORDER:
                for entry in groups[category]:
                    f.write(entry + "\n")
                    
        print(f"成功：已整合 4GTV 與 Smart 列表，並完成分類存檔。")

    except Exception as e:
        print(f"執行出錯: {e}")

if __name__ == "__main__":
    run()

