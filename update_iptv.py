import requests
import re
import os
from urllib.parse import urlparse

# ========= 基本設定 =========
INDEX_URL = "https://iptv-org.github.io/iptv/index.country.m3u"
OUTPUT_MAIN = "4gtv.m3u"
OUTPUT_THAI = "Thailand.m3u"
YOUTUBE_FILE = "youtube 新聞.m3u"

TIMEOUT = 8   # 驗流 timeout
HEADERS = {"User-Agent": "Mozilla/5.0 IPTV-Checker"}

# ========= 分類順序 =========
CATEGORY_ORDER = [
    "YOUTUBE油管新聞",
    "新聞財經",
    "綜合",
    "衛視ipv4",
    "Thailand",
    "戲劇、電影與紀錄片",
    "兒童與青少年",
    "音樂綜藝",
    "運動健康生活",
    "其它"
]

groups = {k: [] for k in CATEGORY_ORDER}


# ========= 工具函式 =========
def fetch_m3u(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text.splitlines()
    except:
        return []


def find_thailand_m3u():
    lines = fetch_m3u(INDEX_URL)
    for l in lines:
        if "thailand.m3u" in l.lower() and l.startswith("http"):
            return l.strip()
    return "https://iptv-org.github.io/iptv/countries/th.m3u"


def stream_alive(url):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True
        )
        return r.status_code == 200
    except:
        return False


def set_group(info, group):
    if 'group-title="' in info:
        return re.sub(r'group-title="[^"]+"', f'group-title="{group}"', info)
    return info.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{group}"')


def classify(info):
    text =