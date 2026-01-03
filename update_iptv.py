import os
import re

SMART = "smart.m3u"
THAI = "thailand.m3u"
OUTPUT = "smart.m3u"

ORDER = [
    "YOUTUBE油管新聞",
    "新聞財經",
    "綜合",
    "Thailand 🇹🇭",
    "歷年春晚",
    "戲劇、電影與紀錄片",
    "兒童與青少年",
    "音樂綜藝",
    "運動健康生活"
]

def parse_m3u(path):
    groups = {}
    header = "#EXTM3U"
    if not os.path.exists(path):
        return header, groups

    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTM3U"):
            header = lines[i]
            i += 1
            continue

        if lines[i].startswith("#EXTINF"):
            info = lines[i]
            url = lines[i + 1]
            grp = re.search(r'group-title="([^"]+)"', info)
            grp = grp.group(1) if grp else "其他"
            groups.setdefault(grp, []).append((info, url))
            i += 2
        else:
            i += 1
    return header, groups

def run():
    header, smart_groups = parse_m3u(SMART)
    _, thai_groups = parse_m3u(THAI)

    # Thailand 強制修正群組名稱
    thai_list = []
    for g in thai_groups.values():
        for info, url in g:
            info = re.sub(
                r'group-title="[^"]+"',
                'group-title="Thailand 🇹🇭"',
                info
            )
            thai_list.append((info, url))

    smart_groups["Thailand 🇹🇭"] = thai_list

    seen = set()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(header + "\n")

        for cat in ORDER:
            if cat not in smart_groups:
                continue
            for info, url in smart_groups[cat]:
                if url in seen:
                    continue
                seen.add(url)
                f.write(info + "\n")
                f.write(url + "\n")

    print("✅ smart.m3u 已合併 Thailand 🇹🇭 並更新完成")

if __name__ == "__main__":
    run()