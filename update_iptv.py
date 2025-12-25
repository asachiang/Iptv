import requests

def run():
    url = "https://jody.im5k.fun/4gtv.m3u"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        # 直接把原檔內容存下來
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(r.text)
    except:
        pass

if __name__ == "__main__":
    run()

