import requests
import re

def is_alive(url):
    try:
        r = requests.get(url, timeout=3, stream=True)
        return r.status_code in [200, 206]
    except:
        return False

def run():
    sources = [
        {"c": "台灣", "u": "https://iptv-org.github.io/iptv/countries/tw.m3u"},
        {"c": "香港", "u": "https://iptv-org.github.io/iptv/countries/hk.m3u"},
        {"c": "泰國", "u": "https://iptv-org.github.io/iptv/countries/th.m3u"},
        {"c": "緬甸", "u": "https://iptv-org.github.io/iptv/countries/mm.m3u"}
    ]
    final = ["#EXTM3U"]
    for s in sources:
        try:
            r = requests.get(s['u'], timeout=20)
            if r.status_code != 200: continue
            lines = r.text.split('\n')
            info = ""
            for l in lines:
                l = l.strip()
                if l.startswith("#EXTINF"):
                    clean = re.sub(r'group-title="[^"]*"', '', l)
                    info = clean.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{s["c"]}"')
                elif l.startswith("http") and info:
                    print(f"Checking {s['c']}: {l[:40]}...")
                    if is_alive(l):
                        final.append(info + "\n" + l)
                    info = ""
        except:
            continue
    with open("international_tv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final))

if __name__ == "__main__":
    run()

