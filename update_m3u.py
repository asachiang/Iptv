        if res.status_code == 200:
            # 以下內容都需要縮進
            lines = res.text.splitlines()
            i = 0

            while i < len(lines):
                if lines[i].startswith("#EXTINF"):
                    extinf = lines[i]
                    url = lines[i + 1] if i + 1 < len(lines) else ""

                    # 移除舊 group-title
                    extinf = re.sub(r'\s*group-title="[^"]*"', '', extinf)

                    # 確保有 -1
                    if not extinf.startswith("#EXTINF:-1"):
                        extinf = extinf.replace("#EXTINF:", "#EXTINF:-1 ")

                    # 插入 youtube 新聞
                    extinf = extinf.replace(
                        "#EXTINF:-1 ",
                        '#EXTINF:-1 group-title="youtube 新聞" ',
                        1
                    )

                    results["youtube 新聞"].append(f"{extinf}\n{url}")
                    i += 2
                else:
                    i += 1

            print(f"✅ YouTube 新聞頻道數：{len(results['youtube 新聞'])}")
        else:
            print(f"❌ YouTube 讀取失敗：{res.status_code}")
