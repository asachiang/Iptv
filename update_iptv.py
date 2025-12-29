import requests
import os

SOURCE_URL = "https://iptv-org.github.io/iptv/index.m3u"
OUTPUT_DIR = "output"

RULES = {
    "taiwan.m3u": ["tvg-country=\"TW\"", "Taiwan", "台灣", "台視", "中視", "民視"],
    "hongkong.m3u": ["tvg-country=\"HK\"", "Hong Kong", "香港", "TVB", "翡翠"],
    "thailand.m3u": ["tvg-country=\"TH\"", "Thailand", "泰國", "Thai"]
}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Downloading source m3u...")
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    lines = r.text.splitlines()

    outputs = {name: ["#EXTM3U"] for name in RULES}

    extinf = ""
    for line in lines:
        if line.startswith("#EXTINF"):
            extinf = line
        elif line.startswith("http") and extinf:
            text = extinf + line
            for out, keywords in RULES.items():
                if any(k.lower() in text.lower() for k in keywords):
                    outputs[out].append(extinf)
                    outputs[out].append(line)
            extinf = ""

    for name, content in outputs.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"Generated {path} ({len(content)//2} channels)")

if __name__ == "__main__":
    main()
