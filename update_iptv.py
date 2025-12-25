import requests
import re

def run():
    # 整合多個高品質來源
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際綜合源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]
    
    # 您要求的排序順序
    PREFERRED_ORDER = ["台灣", "香港", "新聞", "綜合", "體育", "電影", "戲劇", "兒童", "緬甸", "其他"]
    
    groups = {name: [] for name in PREFERRED_ORDER}
    unique_urls = set() # 用於去重，防止重複頻道佔空間
    header = "#EXTM3U"

    for src in sources:
        try:
            print(f"正在抓取 {src['name']}...")
            r = requests.get(src['url'], timeout=30)
            r.raise_for_status()
            r.encoding = 'utf-8'
            
            # 處理部分來源可能存在的換行符號問題
            content = r.text.replace('\r\n', '\n')
            lines = content.splitlines()

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF"):
                    info_line = line
                    # 尋找下一行非空的 URL
                    url_line = ""
                    next_idx = i + 1
                    while next_idx < len(lines):
                        if lines[next_idx].strip() and not lines[next_idx].startswith("#"):
                            url_line = lines[next_idx].strip()
                            break
                        next_idx += 1
                    
                    if url_line and url_line not in unique_urls:
                        unique_urls.add(url_line)
                        
                        # 提取分類與名稱進行關鍵字比對
                        full_text = (info_line + url_line).lower()
                        
                        # 判定分類邏輯
                        target_key = "其他"
                        
                        # 優先判定國家地區
                        if any(k in full_text for k in ["myanmar", "burma", "緬甸"]):
                            target_key = "緬甸"
                        elif any(k in full_text for k in ["hong kong", "hk", "香港", "鳳凰", "hoy"]):
                            target_key = "香港"
                        elif "taiwan" in full_text or "台灣" in full_text or "4gtv" in full_text:
                            target_key = "台灣"
                        else:
                            # 判定一般分類
                            for order_name in PREFERRED_ORDER:
                                if order_name in info_line:
                                    target_key = order_name
                                    break
                        
                        groups[target_key].append(f"{info_line}\n{url_line}")
                    i = next_idx
                else:
                    i += 1
        except Exception as e:
            print(f"抓取 {src['name']} 失敗: {e}")

    # 按順序存檔
    with open("4gtv.m3u", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for category in PREFERRED_ORDER:
            if groups[category]:
                # 加入分類註解，方便在部分播放器查看
                print(f"寫入分類: {category} ({len(groups[category])} 個頻道)")
                for entry in groups[category]:
                    f.write(entry + "\n")
                    
    print("所有頻道已整合完成並去重！")

if __name__ == "__main__":
    run()

