import requests

def download_and_save(urls):
    combined_content = "#EXTM3U\n"
    
    for label, url in urls.items():
        try:
            print(f"正在抓取 {label}...")
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                # 移除每個檔案的 #EXTM3U 標頭再合併
                content = r.text.replace("#EXTM3U", "").strip()
                combined_content += f"\n{content}"
        except:
            print(f"{label} 抓取失敗")
            
    # 儲存為一個總表
    with open("international_list.m3u", "w", encoding="utf-8") as f:
        f.write(combined_content)

if __name__ == "__main__":
    # 您可以在這裡加入更多想要抓取的國際來源網址
    target_urls = {
        "Global": "https://iptv-org.github.io/iptv/index.m3u",
        "News": "https://iptv-org.github.io/iptv/categories/news.m3u",
        "Sports": "https://iptv-org.github.io/iptv/categories/sports.m3u"
    }
    download_and_save(target_urls)

