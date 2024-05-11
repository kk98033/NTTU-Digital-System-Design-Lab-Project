@echo off
chcp 65001

echo 正在檢查虛擬環境...
if exist ".\venv\" (
    echo 找到虛擬環境，正在激活...
    call .\venv\Scripts\activate
    
) else (
    echo 當前目錄未找到虛擬環境，正在檢查上一層目錄...
    cd ..
    if exist ".\venv\" (
        echo 找到虛擬環境，正在激活...
        call .\venv\Scripts\activate
    ) else (
        echo 在上一層目錄也未找到虛擬環境。
        exit /b
    )

    echo 正在啟動 API...
    python .\NTTU-Digital-System-Design-Lab-Project\chat_api.py
)

echo 按任意鍵退出...
pause