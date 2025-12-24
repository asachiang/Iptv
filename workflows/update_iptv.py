import requests
import os

M3U_URL = "https://jody.im5k.fun/4gtv.m3u"
CATEGORIES = {
    "台新聞": ["新聞", "東森", "中天", "TVBS", "三立", "民視"],
    "香港新聞": ["香港", "HK", "鳳凰", "有線"],
    "泰國新聞": ["Thailand", "泰國", "Thai"],
    "綜合": ["綜合", "綜藝", "電影", "戲劇"],
}

def parse_and_save():
    try:
        response = requests.get(M3U_URL, timeout=30)
        response.raise_for_status()
        lines = response.text.split('\n')
    except Exception as e:
        print(f"下載失敗: {e}")
        return

    header = "#EXTM3U"
    organized = {k: [] for k in CATEGORIES.items()}
    organized["其它"] = []

    temp_info = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            temp_info = line
        elif line.startswith("http") and temp_info:
            assigned = False
            for cat, keywords in CATEGORIES.items():
                if any(k.lower() in temp_info.lower() for k in keywords):
                    organized[cat].append(f"{temp_info}\n{line}")
                    assigned = True
                    break
            if not assigned:
                organized["其它"].append(f"{temp_info}\n{line}")
            temp_info = ""

    # 儲存個別分類檔案
    for cat, items in organized.items():
        with open(f"{cat}.m3u", "w", encoding="utf-8") as f:
            f.write(f"{header}\n")
            f.write("\n".join(items))
    
    # 儲存總表
    with open("all.m3u", "w", encoding="utf-8") as f:
        f.write(f"{header}\n")
        for items in organized.values():
            if items:
                f.write("\n".join(items) + "\n")

if __name__ == "__main__":
    parse_and_save()
                if any(k.lower() in temp_info.lower() for k in keywords):
                    organized[cat].append(f"{temp_info}\n{line}")
                    assigned = True
                    break
            if not assigned:
                organized["其它"].append(f"{temp_info}\n{line}")
            temp_info = ""

    # 儲存個別分類檔案
    for cat, items in organized.items():
        with open(f"{cat}.m3u", "w", encoding="utf-8") as f:
            f.write(f"{header}\n")
            f.write("\n".join(items))
    
    # 儲存總表
    with open("all.m3u", "w", encoding="utf-8") as f:
        f.write(f"{header}\n")
        for items in organized.values():
            if items:
                f.write("\n".join(items) + "\n")

if __name__ == "__main__":
    parse_and_save()
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

