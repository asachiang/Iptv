import requests

def update_list():
    # 1. 設定來源網址
    source_url = "https://jody.im5k.fun/4gtv.m3"
    
    try:
        # 2. 下載原始清單
        response = requests.get(source_url, timeout=30)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            print("下載失敗")
            return
            
        lines = response.text.split('\n')
        
        # 3. 解析 M3U 內容
        # 結構為：一個 #EXTINF 配一個網址
        channels = []
        temp_info = ""
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF"):
                temp_info = line
            elif line.startswith("http") and temp_info:
                channels.append({"info": temp_info, "url": line})
                temp_info = ""

        # 4. 定義你的分類關鍵字
        # 你可以在這裡自由增加或修改關鍵字
        categories = {
            "台灣新聞": ["新聞", "東森", "TVBS", "中天", "三立", "民視", "年代", "壹電視"],
            "香港新聞": ["香港", "翡翠", "鳳凰", "RTHK", "Viu"],
            "綜合": ["綜合", "戲劇", "電影", "綜藝"],
            "其他": [] # 沒被分到的放這裡
        }

        # 5. 開始根據關鍵字分類
        sorted_output = []
        used_indices = set()

        for cat_name, keywords in categories.items():
            sorted_output.append(f"#EXTINF:-1,--- 【 {cat_name} 】 ---")
            sorted_output.append("https://raw.githubusercontent.com/asachiang/iptv/main/logo.png") # 裝飾用連結
            
            for i, ch in enumerate(channels):
                if i in used_indices: continue
                
                # 如果是"其他"，就放剩下的；否則檢查關鍵字
                if cat_name == "其他" or any(k in ch["info"] for k in keywords):
                    sorted_output.append(ch["info"])
                    sorted_output.append(ch["url"])
                    used_indices.add(i)

        # 6. 儲存成新的檔案
        with open("iptv.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(sorted_output))
        
        print("更新成功！")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    update_list()
