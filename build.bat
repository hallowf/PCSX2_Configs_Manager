@echo off
echo upx dir is %UPX_DIR%
pyinstaller --noconfirm --log-level=WARN ^
    --upx-dir=R:\Software\UPX ^
    --onefile ^
    --icon="manager.ico" ^
    --name="Manager" ^
    --uac-admin ^
    main.py
