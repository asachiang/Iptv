import requests
import os
import time

BASE = "https://iptv-org.github.io/iptv/countries/"
OUTPUT = "output"
TIMEOUT = 8

COUNTRIES = {
    "taiwan": ["tw.m3u", "4gtv.m3u"],
    "hongkong": ["hk.m3u"],
    "thailand": ["th.m3u"]
}

NEWS_WIRELESS = ["台視", "中視", "華視", "公視"]
NEWS_KEYWORDS = ["news", "新聞", "TVBS", "CNN", "BBC"]
SPORTS_KEYWORDS = ["sport", "體育", "ESPN", "FOX", "ELEVEN", "DAZN"]

def fetch(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text.splitlines()

def alive(url):
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code < 400
    except:
        return False

def classify(extinf, url):
    text = (extinf + url).lower()

    if any(k.lower() in text for k in SPORTS_KEYWORDS):
        return "sports"

    if any(k.lower() in text for k in NEWS_KEYWORDS):
        if any(k in text for k in NEWS_WIRELESS):
            return "news_wireless"
        return "news"

    return "other"

def main():
    os.makedirs(OUTPUT, exist_ok=True)

    for country, sources in COUNTRIES.items():
        buckets = {
            "news_wireless": ["#EXTM3U"],
            "news": ["#EXTM3U"],
            "sports": ["#EXTM3U"],
            "other": ["#EXTM3U"]
        }

        for src in sources:
            print(f"{country}: loading {src}")
            if src.startswith("http") or src.endswith(".m3u") and src != "4gtv.m3u":
                lines = fetch(BASE + src) if src != "4gtv.m3u" else []
            if src == "4gtv.m3u" and os.path.exists("4gtv.m3u"):
                with open("4gtv.m3u", encoding="utf-8") as f:
                    lines = f.read().splitlines()

            extinf = ""
            for line in lines:
                if line.startswith("#EXTINF"):
                    extinf = line
                elif line.startswith("http") and extinf:
                    if alive(line):
                        cat = classify(extinf, line)
                        buckets[cat].extend([extinf, line])
                    extinf = ""
                    time.sleep(0.2)

        for cat, content in buckets.items():
            if len(content) <= 1:
                continue

            name = f"{country}_{cat}.m3u".replace("_news_wireless", "_news_wireless")
            path = os.path.join(OUTPUT, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))

            print(f"✓ {path} ({len(content)//2})")

if __name__ == "__main__":
    main()
