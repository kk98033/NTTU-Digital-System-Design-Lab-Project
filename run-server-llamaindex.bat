@echo off
chcp 65001
echo 啟動虛擬環境...
call ..\venv\Scripts\activate

echo 啟動伺服器...
python server-with-llamaindex-api.py

echo 伺服器已啟動。
echo 退出虛擬環境...
call ..\venv\Scripts\deactivate

pause