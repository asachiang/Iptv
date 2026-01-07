import requests

def fetch_content(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text.splitlines()
    except Exception as e:
        print(f"抓取失敗: {e}")
        return []

def run():
    # 指定來源網址
    url = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"
    
    # 初始化分類容器
    categories = {
        "Litv立視": [],
        "亞太GT": [],
        "體育兢技": []
    }

    lines = fetch_content(url)
    
    # 解析邏輯
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            info = line
            link = lines[i+1] if (i + 1) < len(lines) else ""
            
            # 依照關鍵字分類
            if "Litv" in info or "立視" in info:
                categories["Litv立視"].append(f"{info}\n{link}")
            elif "亞太" in info or "GT" in info:
                categories["亞太GT"].append(f"{info}\n{link}")
            elif any(k in info for k in ["體育", "運動", "兢技"]):
                categories["體育兢技"].append(f"{info}\n{link}")
            
            i += 2
        else:
            i += 1

    # 嚴格按照指定順序輸出
    output_order = ["Litv立視", "亞太GT", "體育兢技"]
    
    with open("custom_list.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for key in output_order:
            if categories[key]:
                f.write(f"### {key} ###\n") # 加入分類標籤方便查看
                f.write("\n".join(categories[key]) + "\n")

    print("✅ 腳本執行完畢：已產生 custom_list.m3u")

if __name__ == "__main__":
    run()
