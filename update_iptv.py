import requests
import re
import os

TIMEOUT = 8

# ======================
# 基本工具
# ======================
def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text.splitlines()
    except Exception as e:
        print(f"❌ 抓取失敗: {url} {e}")
        return []

def is_valid_stream(url):
    if not url.startswith(("http://", "https://")):
        return False
    bad = ["youtube", ".mp4", ".mkv", ".avi", "rtmp", "radio"]
    return not any(b in url.lower() for b in bad)

def head_check(url):
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code < 400
    except:
        return False

# ======================
# 分類判斷
# ======================
def classify(text):
    t = text.upper()
    if "春晚" in t:
        return "歷年春晚"
    if any(k in t for k in ["NEWS", "新聞", "財經"]):
        return "新聞財經"
    if any(k in t for k in ["MOVIE", "DRAMA", "電影", "戲劇", "紀錄"]):
        return "戲劇、電影與紀錄片"
    if any(k in t for k in ["KIDS", "兒童", "卡通"]):
        return "兒童與青少年"
    if any(k in t for k in ["MUSIC", "綜藝", "音樂"]):
        return "音樂綜藝"
    if any(k in t for k in ["SPORT", "運動", "健康"]):
        return "運動健康生活"
    return "綜合"

# ======================
# Thailand 擷取
# ======================
def extract_thailand():
    url = "https://iptv-org.github.io/iptv/index.country.m3u"
    lines = fetch_m3u(url)

    seen = set()
    out = {"Thailand": []}

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF") and "THAILAND" in lines[i].upper():
            info = lines[i]
            j = i + 1
            while j < len(lines) and not lines[j].startswith("#EXTINF"):
                stream = lines[j].strip()
                if is_valid_stream(stream) and stream not in seen:
                    if head_check(stream):
                        seen.add(stream)
                        info = re.sub(
                            r'group-title="[^"]+"',
                            'group-title="Thailand"',
                            info
                        )
                        out["Thailand"].append(f"{info}\n{stream}")
                j += 1
            i = j
        else:
            i += 1
    return out

# ======================
# 主程式
# ======================
def run():
    OUTPUT_THAI = "thailand.m3u"
    HEADER = "#EXTM3U"

    groups = {
        "YOUTUBE油管新聞": [],
        "新聞財經": [],
        "綜合": [],
        "Thailand": [],
        "歷年春晚": [],
        "戲劇、電影與紀錄片": [],
        "兒童與青少年": [],
        "音樂綜藝": [],
        "運動健康生活": []
    }

    # --- Thailand ---
    thai = extract_thailand()
    groups["Thailand"].extend(thai["Thailand"])

    # --- 輸出 Thailand ---
    with open(OUTPUT_THAI, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for item in groups["Thailand"]:
            f.write(item + "\n")

    print(f"✅ Thailand 頻道完成：{len(groups['Thailand'])} 條")
    print(f"📄 輸出檔案：{OUTPUT_THAI}")

if __name__ == "__main__":
    run()