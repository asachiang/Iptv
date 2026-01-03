import requests
import re
import os

def fetch_m3u(url):
    """抓取 M3U 檔案"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text.splitlines()
    except Exception as e:
        print(f"無法抓取 {url}: {e}")
        return []

def validate_url(url):
    """嚴格篩選：檢查連結是否可用 (Timeout 3秒)"""
    try:
        # 使用 head 請求節省流量
        response = requests.head(url, timeout=3, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def run():
    # 來源網址
    URL_4GTV = "https://jody.im5k.fun/4gtv.m3u"
    URL_SMART = "https://jody.im5k.fun/smart.m3u"
    URL_IPTV_ORG = "https://iptv-org.github.io/iptv/index.country.m3u"
    
    # 本地檔案
    youtube_file = "youtube 新聞.m3u"
    
    # 新的分類定義
    CAT_NEWS = ["新聞", "財經"]
    CAT_GENERAL = ["綜合"]
    CAT_DRAMA = ["戲劇", "電影", "紀錄片"]
    CAT_KIDS = ["兒童", "青少年"]
    CAT_MUSIC = ["音樂", "綜藝"]
    CAT_SPORT = ["運動", "健康", "生活"]

    try:
        # 1. 抓取 4GTV 並分類
        lines_4gtv = fetch_m3u(URL_4GTV)
        groups = { "NEWS": [], "GEN": [], "DRAMA": [], "KIDS": [], "MUSIC": [], "SPORT": [], "OTHER": [] }
        
        i = 0
        while i < len(lines_4gtv):
            line = lines_4gtv[i].strip()
            if line.startswith("#EXTINF"):
                info, url_line = line, lines_4gtv[i+1].strip()
                if any(k in info for k in CAT_NEWS): groups["NEWS"].append(f"{info}\n{url_line}")
                elif any(k in info for k in CAT_GENERAL): groups["GEN"].append(f"{info}\n{url_line}")
                elif any(k in info for k in CAT_DRAMA): groups["DRAMA"].append(f"{info}\n{url_line}")
                elif any(k in info for k in CAT_KIDS): groups["KIDS"].append(f"{info}\n{url_line}")
                elif any(k in info for k in CAT_MUSIC): groups["MUSIC"].append(f"{info}\n{url_line}")
                elif any(k in info for k in CAT_SPORT): groups["SPORT"].append(f"{info}\n{url_line}")
                else: groups["OTHER"].append(f"{info}\n{url_line}")
                i += 2
            else: i += 1

        # 2. 處理 Thailand 頻道 (從 iptv-org 篩選並驗證)
        print("正在篩選並驗證 Thailand 頻道...")
        lines_org = fetch_m3u(URL_IPTV_ORG)
        th_list = []
        for j, line in enumerate(lines_org):
            if 'group-title="Thailand"' in line:
                url = lines_org[j+1].strip()
                if validate_url(url): # 執行嚴格篩選
                    th_list.append(f"{line}\n{url}")
        
        with open("thailand.m3u", "w", encoding="utf-8") as tf:
            tf.write("#EXTM3U\n" + "\n".join(th_list))

        # 3. 處理 Smart.m3u (衛視、央視、4K)
        smart_lines = fetch_m3u(URL_SMART)
        ws_ipv4, ys_ipv4, k48_list = [], [], []
        for j, line in enumerate(smart_lines):
            if line.startswith("#EXTINF"):
                url = smart_lines[j+1].strip()
                if "衛視" in line and "IPV4" in line.upper(): ws_ipv4.append(f"{line}\n{url}")
                elif "央視" in line and "IPV4" in line.upper(): ys_ipv4.append(f"{line}\n{url}")
                elif any(k in line.upper() for k in ["4K", "8K"]): k48_list.append(f"{line}\n{url}")

        # 4. 讀取 YouTube
        yt_content = []
        if os.path.exists(youtube_file):
            with open(youtube_file, "r", encoding="utf-8") as yf:
                yt_content = [l.strip() for l in yf if not l.startswith("#EXTM3U") and l.strip()]

        # 5. 寫入最終 4gtv.m3u
        with open("4gtv.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("\n".join(yt_content) + "\n") # YouTube
            for cat in ["NEWS", "GEN", "DRAMA", "KIDS", "MUSIC", "SPORT", "OTHER"]:
                f.write("\n".join(groups[cat]) + "\n")
            f.write("\n".join(th_list) + "\n") # Thailand
            f.write("\n".join(ws_ipv4) + "\n") # 衛視
            f.write("\n".join(ys_ipv4) + "\n") # 央視
            f.write("\n".join(k48_list) + "\n") # 4K8K

        print("✅ 腳本執行成功！thailand.m3u 與 4gtv.m3u 已同步。")
    except Exception as e:
        print(f"❌ 錯誤：{e}")

if __name__ == "__main__":
    run()
