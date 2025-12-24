import requests

M3U_URL = "https://jody.im5k.fun/4gtv.m3u"
CATEGORIES = {
    "台新聞": ["新聞", "東森", "中天", "TVBS", "三立", "民視"],
    "香港新聞": ["香港", "HK", "鳳凰", "有線"],
    "泰國新聞": ["Thailand", "泰國", "Thai"],
    "綜合": ["綜合", "綜藝", "電影", "戲劇"],
}

def parse_and_save():
    try:
        r = requests.get(M3U_URL, timeout=30)
        r.raise_for_status()
        lines = r.text.split('\n')
    except:
        return

    header = "#EXTM3U"
    organized = {k: [] for k in CATEGORIES.keys()}
    organized["其它"] = []
    temp = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#EXTM3U"): continue
        if line.startswith("#EXTINF"):
            temp = line
        elif line.startswith("http") and temp:
            assigned = False
            for cat, keywords in CATEGORIES.items():
                if any(k.lower() in temp.lower() for k in keywords):
                    organized[cat].append(f"{temp}\n{line}")
                    assigned = True
                    break
            if not assigned:
                organized["其它"].append(f"{temp}\n{line}")
            temp = ""

    for cat, items in organized.items():
        with open(f"{cat}.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n" + "\n".join(items))
    
    with open("all.m3u", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for items in organized.values():
            if items: f.write("\n".join(items) + "\n")

if __name__ == "__main__":
    parse_and_save()
