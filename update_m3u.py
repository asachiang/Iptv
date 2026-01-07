import requests
import re
import urllib.parse

# ========= 來源 =========
yt_filename = urllib.parse.quote("youtube新聞.m3u")
SOURCE_YOUTUBE = f"https://raw.githubusercontent.com/asachiang/iptv/main/{yt_filename}"
SOURCE_4GTV = "https://raw.githubusercontent.com/LinWei630718/iptvtw/da39d222bb26830efd211e74addd6e5f490dc63d/4gtv.m3u"

# ========= 分類順序 =========
TARGET_ORDER = ["youtube 新聞", "Litv立視", "亞太GT", "體育兢技", "兒童卡通"]

# ========= 4GTV 分類規則 =========
CATEGORY_MAP_4GTV = {
    "Litv立視": ["litv", "立視"],
    "亞太GT": ["亞太", "gt"],
    "體育兢技": ["體育", "兢技", "運動", "sports"],
    "兒童卡通": ["兒童", "卡通", "kids", "anime"]
}

def main():
    results = {cat: [] for cat in TARGET_ORDER}

    # ===== YouTube 新聞：整個列表全收 =====
    print(f"抓取 YouTube 列表：{SOURCE_YOUTUBE}")
    try:
        res = requests.get(SOURCE_YOUTUBE, timeout=15)
        res.encoding = "utf-8"

        if res.status_code == 200:
            lines = res.text.splitlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith("#EXTINF"):
                    extinf = lines[i]
                    url = lines[i + 1] if i + 1 < len(lines) else ""

                    # 移除舊 group-title
                    extinf = re.sub(r'group-title="[^"]*"', '', extinf)

                    # 強制指定 youtube 新聞
                    extinf = extinf.replace(
                        "#EXTINF:",
                        '#EXTINF:-1 group-title="youtube 新聞",'
                    )

                    results["youtube 新聞"].append(f"{extinf}\n{url}")
                    i += 2
                else:
                    i += 1

            print(f"✅ YouTube 新聞頻道數：{len(results['youtube 新聞'])}")
        else:
            print(f"❌ YouTube 讀取失敗：{res.status_code}")
    except Exception as e:
        print(f"❌ YouTube 發生錯誤：{e}")

    # ===== 4GTV =====
    try:
        res = requests.get(SOURCE_4GTV, timeout=15)
        res.encoding = "utf-8"

        if res.status_code == 200:
            items = re.findall(r'(#EXTINF:.*?\nhttp.*)', res.text)
            for item in items:
                m = re.search(r'group-title="([^"]+)"', item, re.IGNORECASE)
                group = m.group(1).lower() if m else ""

                for label, keywords in CATEGORY_MAP_4GTV.items():
                    if any(k in group for k in keywords):
                        results[label].append(item)
                        break
    except Exception as e:
        print(f"❌ 4GTV 發生錯誤：{e}")

    # ===== 輸出 =====
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for label in TARGET_ORDER:
            for ch in results[label]:
                f.write("\n" + ch.strip() + "\n")

    print("\n🎉 完成：playlist.m3u 已生成")

if __name__ == "__main__":
    main()