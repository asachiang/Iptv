import requests
import re
import os

# 設定來源與分類關鍵字
M3U_URL = "https://jody.im5k.fun/4gtv.m3u"
CATEGORIES = {
    "台新聞": ["新聞", "東森", "中天", "TVBS", "三立", "民視"],
    "香港新聞": ["香港", "HK", "鳳凰", "有線"],
    "泰國新聞": ["Thailand", "泰國", "Thai"],
    "綜合": ["綜合", "綜藝", "電影", "戲劇"],
}

def download_m3u(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_and_save(content):
    lines = content.split('\n')
    header = lines[0] # #EXTM3U
    
    # 建立一個容器存放各類別內容
    organized = {k: [] for k in CATEGORIES.keys()}
    organized["其它"] = []

    current_info = None
    
    for line in lines[1:]:
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http"):
            # 判斷分類
            assigned = False
            for cat, keywords in CATEGORIES.items():
                if any(k.lower() in current_info.lower() for k in keywords):
                    organized[cat].append(f"{current_info}\n{line}")
                    assigned = True
                    break
            if not assigned:
                organized["其它"].append(f"{current_info}\n{line}")

    # 寫入檔案
    for cat, items in organized.items():
        filename = f"{cat}.m3u"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{header}\n")
            f.write("\n".join(items))
    
    # 同時產出一個合併但已分類的總表
    with open("all.m3u", "w", encoding="utf-8") as f:
        f.write(f"{header}\n")
        for cat in organized:
            f.write("\n".join(organized[cat]) + "\n")

if __name__ == "__main__":
    print("正在下載直播源...")
    raw_content = download_m3u(M3U_URL)
    print("正在進行分類...")
    parse_and_save(raw_content)
    print("處理完成！")
                    organized[cat].append(f"{current_info}\n{line}")
                    assigned = True
                    break
            if not assigned:
                organized["其它"].append(f"{current_info}\n{line}")

    # 寫入檔案
    for cat, items in organized.items():
        filename = f"{cat}.m3u"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{header}\n")
            f.write("\n".join(items))
    
    # 同時產出一個合併但已分類的總表
    with open("all.m3u", "w", encoding="utf-8") as f:
        f.write(f"{header}\n")
        for cat in organized:
            f.write("\n".join(organized[cat]) + "\n")

if __name__ == "__main__":
    print("正在下載直播源...")
    raw_content = download_m3u(M3U_URL)
    print("正在進行分類...")
    parse_and_save(raw_content)
    print("處理完成！")
                f.write(info + "\n" + link + "\n")

