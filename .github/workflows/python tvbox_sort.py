# -*- coding: utf-8 -*-

INPUT_FILE = "input.txt"     # 原始播放列表
OUTPUT_FILE = "tvbox.txt"    # TVBox 輸出

groups = {
    "📰新闻": ["新闻", "News", "CNN", "BBC", "Bloomberg", "东森新闻", "财经"],
    "📺综合": ["综合", "HD", "东森", "三立", "民视", "八大", "中视", "TVB"],
    "🏀体育": ["体育", "Sports", "NBA", "CCTV5", "足球", "网球"],
    "🎬电影": ["电影", "Movie", "HBO", "CINEMAX", "Star"],
    "👶儿童": ["儿童", "卡通", "Kids", "Animax", "Baby"],
    "🌍纪实": ["Discovery", "NatGeo", "国家地理", "History", "Animal"]
}

result = {k: [] for k in groups}
others = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "," not in line:
            continue

        name, url = line.split(",", 1)
        matched = False

        for group, keys in groups.items():
            if any(k.lower() in name.lower() for k in keys):
                result[group].append(f"{name},{url}")
                matched = True
                break

        if not matched:
            others.append(f"{name},{url}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for group, items in result.items():
        if items:
            f.write(f"{group},#genre#\n")
            for item in items:
                f.write(item + "\n")
            f.write("\n")

    if others:
        f.write("📦其他,#genre#\n")
        for item in others:
            f.write(item + "\n")

print("✅ TVBox 播放列表自動分類完成")
