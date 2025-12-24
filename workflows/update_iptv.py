import requests
url = "https://jody.im5k.fun/4gtv.m3u"
cats = {
    "台新聞": ["新聞", "東森", "中天", "TVBS", "三立", "民視"],
    "香港新聞": ["香港", "HK", "鳳凰", "有線"],
    "泰國新聞": ["Thailand", "泰國", "Thai"],
    "綜合": ["綜合", "綜藝", "電影", "戲劇"]
}
def run():
    try:
        data = requests.get(url).text.split('\n')
    except: return
    res = {k: [] for k in cats}
    res["其它"] = []
    info = ""
    for l in data:
        l = l.strip()
        if l.startswith("#EXTINF"): info = l
        elif l.startswith("http") and info:
            hit = False
            for k, v in cats.items():
                if any(x.lower() in info.lower() for x in v):
                    res[k].append(f"{info}\n{l}"); hit = True; break
            if not hit: res["其它"].append(f"{info}\n{l}")
            info = ""
    for k, v in res.items():
        with open(f"{k}.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n" + "\n".join(v))
if __name__ == "__main__":
    run()
