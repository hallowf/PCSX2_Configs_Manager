@echo off
echo upx dir is %UPX_DIR%
pyinstaller --noconfirm --log-level=WARN ^
    --onefile ^
    --icon="manager.ico" ^
    --name="Manager" ^
    --uac-admin ^
    main.spec
