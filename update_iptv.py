import requests

def parse_and_save():
    # 設定來源與分類
    url = "https://jody.im5k.fun/4gtv.m3u"
    categories = {
        "台新聞": ["新聞", "東森", "中天", "TVBS", "三立", "民視"],
        "香港新聞": ["香港", "HK", "鳳凰", "有線"],
        "泰國新聞": ["Thailand", "泰國", "Thai"],
        "綜合": ["綜合", "綜藝", "電影", "戲劇"]
    }
    
    try:
        response = requests.get(url, timeout=30)
        lines = response.text.split('\n')
    except:
        return

    # 初始化容器
    organized = {name: [] for name in categories.keys()}
    organized["其它"] = []
    
    temp_info = ""
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            temp_info = line
        elif line.startswith("http") and temp_info:
            found = False
            for name, keywords in categories.items():
                if any(k.lower() in temp_info.lower() for k in keywords):
                    organized[name].append(f"{temp_info}\n{line}")
                    found = True
                    break
            if not found:
                organized["其它"].append(f"{temp_info}\n{line}")
            temp_info = ""

    # 儲存檔案
    for name, items in organized.items():
        with open(f"{name}.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n" + "\n".join(items))

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

