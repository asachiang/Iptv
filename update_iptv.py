import requests
import re

def run():
    # 定義多個來源
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    # 您的排序要求，新增了香港與緬甸分類
    PREFERRED_ORDER = ["台灣", "香港", "新聞", "綜合", "體育", "電影", "戲劇", "兒童", "緬甸", "其他"]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    header = "#EXTM3U"

    for src in sources:
        try:
            print(f"正在抓取 {src['name']}...")
            r = requests.get(src['url'], timeout=30)
            r.raise_for_status()
            r.encoding = 'utf-8'
            lines = r.text.splitlines()

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF"):
                    info_line = line
                    url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    
                    # 獲取標籤
                    group_match = re.search(r'group-title="([^"]+)"', info_line)
                    detected_group = group_match.group(1) if group_match else "其他"
                    
                    # 邏輯判斷：根據關鍵字歸類
                    target_key = "其他"
                    
                    # 優先檢查國家/地區關鍵字
                    if "Myanmar" in info_line or "Burma" in info_line:
                        target_key = "緬甸"
                    elif "香港" in detected_group or "Hong Kong" in detected_group or "HK" in detected_group:
                        target_key = "香港"
                    else:
                        # 檢查其餘分類
                        for order_name in PREFERRED_ORDER:
                            if order_name in detected_group:
                                target_key = order_name
                                break
                    
                    groups[target_key].append(f"{info_line}\n{url_line}")
                    i += 2
                else:
                    i += 1
        except Exception as e:
            print(f"抓取 {src['name']} 失敗: {e}")

    # 存檔
    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for category in PREFERRED_ORDER:
            if groups[category]:
                for entry in groups[category]:
                    f.write(entry + "\n")
                    
    print(f"整合整理完成！")

if __name__ == "__main__":
    run()

