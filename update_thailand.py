import requests
import re
import time

SOURCE_URL = "https://iptv-org.github.io/iptv/index.country.m3u"
OUTPUT_FILE = "thailand.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIMEOUT = 10


def fetch_m3u(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text.splitlines()


def is_valid_stream(url):
    if not url.startswith("http"):
        return False
    if not re.search(r"\.(m3u8|ts)", url):
        return False
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code < 400
    except:
        return False


def normalize_extinf(line):
    # 強制 group-title 為 Thailand
    if 'group-title="' in line