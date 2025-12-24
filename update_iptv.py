import requests

def run():
    # 原始來源網址
    url = "https://jody.im5k.fun/4gtv.m3u"
    try:
        # 抓取原檔內容
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        
        # 直接儲存，不對內容做任何改動
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(r.text)
        print("原檔抓取成功")
    except Exception as e:
        print(f"抓取失敗: {e}")

if __name__ == "__main__":
    run()

