import requests
import os

BASE = "https://iptv-org.github.io/iptv/countries/"
OUTPUT_DIR = "output"

COUNTRIES = {
    "taiwan": "tw.m3u",
    "hongkong": "hk.m3u",
    "thailand": "th.m3u"
}

NEWS_KEYWORDS = [
    "news", "新聞", "台視新聞", "中視新聞", "民視新聞",
    "TVBS", "CNN", "BBC", "Bloomberg"
]

def download(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.text.splitlines()

def is_news(text):
    text = text.lower()
    return any(k.lower() in text for k in NEWS_KEYWORDS)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for country, file in COUNTRIES.items():
        print(f"Processing {country}")
        lines = download(BASE + file)

        news = ["#EXTM3U"]
        other = ["#EXTM3U"]

        extinf = ""
        for line in lines:
            if line.startswith("#EXTINF"):
                extinf = line
            elif line.startswith("http") and extinf:
                block = extinf + line
                if is_news(block):
                    news.extend([extinf, line])
                else:
                    other.extend([extinf, line])
                extinf = ""

        with open(f"{OUTPUT_DIR}/{country}_news.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(news))

        with open(f"{OUTPUT_DIR}/{country}_other.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(other))

        print(
            f"{country}: news={len(news)//2}, other={len(other)//2}"
        )

if __name__ == "__main__":
    main()
