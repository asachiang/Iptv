import requests
import re
import os

def fetch_m3u(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text.splitlines()

def run():
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    youtube_file = "youtube 新聞.m3u"

    # 4GTV 分類順序
    PREFERRED_ORDER = [
        "財經新聞", "新聞", "綜合",
        "戲劇、電影", "電影", "戲劇",
        "兒童", "其他"
    ]

    # smart.m3u 指定順序
    SMART_ORDER = [
        "gpt-台湾",
        "gpt-香港",
        "gpt-泰国",
        "gpt-日本",
        "gpt-其他"
    ]

    try:
        # ========= 1️⃣ 處理 4GTV =========
        lines = fetch_m3u(URL_4GTV)
        groups = {k: [] for k in PREFERRED_ORDER}
        header = "#EXTM3U"

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                info = line
                url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

                match = re.search(r'group-title="([^"]+)"', info)
                detected = match.group(1) if match else "其他"

                key = "其他"
                for k in PREFERRED_ORDER:
                    if k in detected:
                        key = k
                        break

                groups[key].append(f"{info}\n{url_line}")
                i += 2
            else:
                if line.startswith("#EXTM3U"):
                    header = line
                i += 1

        # ========= 2️⃣ 讀取 YouTube 新聞 =========
        youtube_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                for line in yf:
                    if not line.startswith("#EXTM3U") and line.strip():
                        youtube_content.append(line.strip())

        # ========= 3️⃣ 處理 smart.m3u（重新排序） =========
  # ========= 3️⃣ 處理 smart.m3u（重新排序，修正版） =========
        smart.m3u（重新排序，修正版） =========
                smart_groups[key].append(f"{info}\n{url_line}")
                i += 2
            else:
                i += 1 ""

                match = re.search(r'group-title="([^"]+)"', info)
                group = match.group(1) if match else "gpt-其他"

                key = "gpt-其他"
for k in SMART_ORDER:
    if k in group:
        key = k
        break
                smart_groups[key].append(f"{info}\n{url_line}")
                i += 2
            else:
                i += 1

        # ========= 4️⃣ 輸出 4gtv.m3u =========
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write(header + "\n")

            # YouTube 新聞置頂
            for line in youtube_content:
                f.write(line + "\n")

            # 4GTV 分類
            for cat in PREFERRED_ORDER:
                for entry in groups[cat]:
                    f.write(entry + "\n")

            # smart.m3u 依指定順序
            for cat in SMART_ORDER:
                for entry in smart_groups[cat]:
                    f.write(entry + "\n")

        # ========= 5️⃣ 輸出 smart_sorted.m3u =========
        with open("smart_sorted.m3u", "w", encoding="utf-8") as sf:
            sf.write("#EXTM3U\n")
            for cat in SMART_ORDER:
                for entry in smart_groups[cat]:
                    sf.write(entry + "\n")

        print("✅ 完成：4gtv.m3u 與 smart_sorted.m3u 已更新")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")

if __name__ == "__main__":
    run()