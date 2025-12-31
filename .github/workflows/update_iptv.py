name: Update IPTV Lists

on:
  schedule:
    # 每天凌晨 00:00 (UTC) 自動執行，你可以根據需求調整
    - cron: '0 16 * * *' 
  workflow_dispatch: # 允許手動點擊按鈕執行

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: 檢出代碼
      uses: actions/checkout@v3

    - name: 設定 Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: 安裝依賴
      run: |
        pip install requests

    - name: 執行更新腳本
      run: python update_iptv.py

    - name: 提交並推送更新
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add smart.m3u 4gtv.m3u
        git commit -m "自動更新 M3U 列表: $(date +'%Y-%m-%d %H:%M')" || exit 0
        git push
