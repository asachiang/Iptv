import requests
import re

def run():
    # 定義國家來源與關鍵字過濾（使用 IPTV-org 的分類連結最為穩定）
    sources = [
        {"country": "台灣", "url": "https://iptv-org.github.io/iptv/countries/tw.m3u"},
        {"country": "香港", "url": "https://iptv-org.github.io/iptv/countries/hk.m3u"},
        {"country": "泰國", "url": "https://iptv-org.github.io/iptv/countries/th.m3u"},
        {"country": "緬甸", "url": "https://iptv-org.github.io/iptv/countries/mm.m3u"}
    ]

    final_content = ["#EXTM3U"]

    for src in sources:
        try:
            print(f"正在抓取 {src['country']}...")
            r = requests.get(src['url'], timeout=30)
            if r.status_code == 200:
                lines = r.text.split('\n')
                current_info = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        # 在標籤中強制加入 group-title，方便播放器分類
                        # 移除原有的 group-title 並加上我們自定義的國家名稱
                        info = re.sub(r'group-title="[^"]*"', '', line)
                        current_info = info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{src["country"]}"')
                    elif line.startswith("http") and current_info:
                        final_content.append(current_info + "\n" + line)
                        current_info = ""
        except Exception as e:
            print(f"{src['country']} 抓取失敗: {e}")

    # 儲存為一個合併檔案
    with open("international_tv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_content))
    print("合併檔案已生成：international_tv.m3u")

if __name__ == "__main__":
    run()

