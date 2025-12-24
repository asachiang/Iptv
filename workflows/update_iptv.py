import requests
import re

# 1. 下載原始檔案
url = "https://jody.im5k.fun/4gtv.m3"
response = requests.get(url)
content = response.text

# 2. 定義分類邏輯 (根據頻道名稱關鍵字)
categories = {
    "台灣新聞": ["新聞", "東森", "TVBS", "中天", "三立"],
    "香港新聞": ["香港", "翡翠", "鳳凰", "RTHK"],
    "綜合": ["綜合", "戲劇", "電影"],
}

# 3. 解析 m3u 並分類
lines = content.split('\n')
header = lines[0] # #EXTM3U
channels = []
current_channel = ""

for line in lines[1:]:
    if line.startswith("#EXTINF"):
        current_channel = line
    elif line.startswith("http"):
        channels.append((current_channel, line))

# 4. 按順序寫入新檔案 (iptv.m3u)
with open("iptv.m3u", "w", encoding="utf-8") as f:
    f.write(header + "\n")
    # 按照分類寫入
    for cat, keywords in categories.items():
        f.write(f"#EXTINF:-1,--- {cat} ---\n")
        f.write("http://placeholder.com\n") # 分隔線標籤
        for info, link in channels:
            if any(kw in info for kw in keywords):
                f.write(info + "\n" + link + "\n")

