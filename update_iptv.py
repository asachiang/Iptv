import requests
import os

SOURCE_URL = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_DIR = "output"

COUNTRIES = {
    "TW": "taiwan.m3u",
    "HK": "hongkong.m3u",
    "TH": "thailand.m3u"
}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Downloading source m3u...")
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    lines = r.text.splitlines()

    buffers = {c: ["#EXTM3U"] for c in COUNTRIES}

    extinf = None
    for line in lines:
        if line.startswith("#EXTINF"):
            extinf = line
        elif line.startswith("http") and extinf:
            for c in COUNTRIES:
                if f'tvg-country="{c}"' in extinf:
                    buffers[c].append(extinf)
                    buffers[c].append(line)
            extinf = None

    for c, filename in COUNTRIES.items():
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(buffers[c]))
        print(f"Generated {path}")

if __name__ == "__main__":
    main()
