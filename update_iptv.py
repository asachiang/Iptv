import requests
import re
import os

def fetch_m3u(url):
    """抓取 M3U"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text.splitlines()
    except Exception as e:
        print(f"❌ 抓取失敗 {url}: {e}")
        return []

def run():
    # ===== 來源 =====
    sources = [
        {"name": "台灣4GTV", "url": "https://jody.im5k.fun/4gtv.m3u"},
        {"name": "香港頻道", "url": "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/HongKong.m3u8"},
        {"name": "國際源", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u"}
    ]

    OUTPUT_FILE = "4gtv.m3u"

    # ===== 分類順序（已排除央视 / 4K8K）=====
    PREFERRED_ORDER = [
        "新聞財經",
        "綜合",
        "衛視IPV4",
        "歷年春晚",
        "戲劇、電影與紀錄片",
        "兒童與青少年",
        "音樂綜藝",
        "運動健康生活"
    ]

    groups = {k: [] for k in PREFERRED_ORDER}
    groups["其他"] = []
    header = "#EXTM3U"

    # ===== 處理來源 =====
    for src in sources:
        print(f"▶ 處理來源：{src['name']}")
        lines = fetch_m3u(src["url"])
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("#EXTINF"):
                info_line = line
                content_lines = []

                j = i + 1
                while j < len(lines) and not lines[j].startswith("#EXTINF"):
                    if lines[j].strip():
                        content_lines.append(lines[j].strip())
                    j += 1

                full_content = "\n".join(content_lines)

                # 頻道名稱 / 分組
                chan_name = info_line.split(",")[-1].upper()
                group_match = re.search(r'group-title="([^"]+)"', info_line)
                original_group = group_match.group(1).upper() if group_match