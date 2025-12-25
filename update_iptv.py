import requests
import re

# 檢測連結是否有效
def is_alive(url):
    try:
        # 使用 stream=True 或 head 請求，只檢查連通性而不下載內容
        r = requests.get(url, timeout=3, stream=True, allow_redirects=True)
        # 只要返回 200 或 206 (部分內容) 都視為有效
        return r.status_code in [200, 206]
    except:
        return False

def run():
    # 改用更穩定的來源或維持 iptv-org
    sources = [
        {"country": "台灣", "url": "https://iptv-org.github.io/iptv/countries/tw.m3u"},
        {"country": "香港", "url": "https://iptv-org.github.io/iptv/countries/hk.m3u"},
        {"country": "泰國", "url": "https://iptv-org.github.io/iptv/countries/th.m3u"},
        {"country": "緬甸", "url": "https://iptv-org.github.io/iptv/countries/mm.m3u"}
    ]

    final_content = ["#EXTM3U"]

    for src in sources:
        try:
            print(f"正在抓取並過濾 {src['country']} 的連結...")
            r = requests.get(src['url'], timeout=30)
            if r.status_code == 200:
                lines = r.text.split('\n')
                current_info = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        info = re.sub(r'group-title="[^"]*"', '', line)
                        current_info = info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{src["country"]}"')
                    elif line.startswith("http") and current_info:
                        # --- 關鍵修正：在此處加入檢測 ---
                        print(f" 正在檢測: {current_info.split(',')[-1]}", end=" ")
                        if is_alive(line):
                            final_content.append(current_info + "\n" + line)
                            print("✅ 有效")
                        else:
                            print("❌ 失效 (跳過)")
                        # ------------------------------
                        current_info = ""
        except Exception as e:
            print(f"{src['country']} 抓取失敗: {e}")

    with open("international_tv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_content))
    print("\n✅ 過濾完成，檔案已更新。")

if __name__ == "__main__":
    run()
                        # 移除原有的 group-title 並加上我們自定義的國家名稱
                        info = re.sub(r'group-title="[^"]*"', '', line)
                        current_info = info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{src["country"]}"')
                    elif line.startswith("http") and current_info:
                        final_content.append(current_info + "\n" + line)
                        current_info = ""
        except Exception as e:
            print(f"{src['country']} 抓取失敗: {e}")

    # 儲存為一個合併檔案
    with open("international_tv.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(final_content))
    print("合併檔案已生成：international_tv.m3u")

if __name__ == "__main__":
    run()

