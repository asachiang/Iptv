import requests
import re

SOURCE_URL = "https://iptv-org.github.io/iptv/index.country.m3u"
OUTPUT_FILE = "thailand.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

TIMEOUT = 8
READ_BYTES = 2048   # 讀前 2KB 判斷是否真有資料


def fetch_m3u(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text.splitlines()


def is_real_stream(url):
    if not url.startswith("http"):
        return False

    if not re.search(r"\.(m3u8|ts)", url.lower()):
        return False

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            stream=True
        )

        if r.status_code >= 400:
            return False

        content_type = r.headers.get("Content-Type", "").lower()

        # m3u8 必須是 playlist
        if url.endswith(".m3u8"):
            chunk = r.raw.read(READ_BYTES, decode_content=True)
            text = chunk.decode("utf-8", errors="ignore")
            return "#EXTM3U" in text or "#EXTINF" in text

        # ts 檔必須能讀到 binary
        if url.endswith(".ts"):
            chunk = r.raw.read(READ_BYTES)
            return len(chunk) > 188  # TS packet size

        return False

    except Exception:
        return False


def normalize_extinf(line):
    if 'group-title="' in line:
        return re.sub(
            r'group-title="[^"]*"',
            'group-title="Thailand"',
            line
        )
    return line.replace(
        "#EXTINF:-1",
        '#EXTINF:-1 group-title="Thailand"'
    )


def run():
    lines = fetch_m3u(SOURCE_URL)

    output = ["#EXTM3U"]
    keep = False
    extinf = ""

    total = 0
    kept = 0

    for line in lines:
        line = line.strip()

        # 找到 Thailand 區段
        if "thailand.m3u" in line.lower():
            keep = True
            continue

        if keep and line.startswith("#EXTINF"):
            extinf = normalize_extinf(line)
            continue

        if keep and line.startswith("http"):
            total += 1
            if is_real_stream(line):
                output.append(extinf)
                output.append(line)
                kept += 1
            extinf = ""

        # 下一個國家出現就結束
        if keep and line.endswith(".m3u") and "thailand" not in line.lower():
            break

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("===== Thailand 嚴格驗流完成 =====")
    print(f"原始頻道數：{total}")
    print(f"保留可播放：{kept}")
    print(f"輸出檔案：{OUTPUT_FILE}")


if __name__ == "__main__":
    run()