import re

with open('input.m3u', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_tw_news = []
output_hk_sports = []
current_info = None

for line in lines:
    if line.startswith('#EXTINF'):
        current_info = line
    elif line.strip() and not line.startswith('#'):
        if 'tvg-country="TW"' in current_info and 'news' in current_info.lower():
            output_tw_news.append(current_info + line)
        if 'tvg-country="HK"' in current_info and 'sports' in current_info.lower():
            output_hk_sports.append(current_info + line)

# 寫出檔案
with open('tw_news.m3u', 'w', encoding='utf-8') as f:
    f.write('#EXTM3U\n' + ''.join(output_tw_news))

with open('hk_sports.m3u', 'w', encoding='utf-8') as f:
    f.write('#EXTM3U\n' + ''.join(output_hk_sports))
