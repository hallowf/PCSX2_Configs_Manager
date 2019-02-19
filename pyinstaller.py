import PyInstaller.__main__
import os

UPX_PATH = os.environ["UPX_PATH"]
CWD = os.path.dirname(os.path.abspath(__file__))


PyInstaller.__main__.run([
        '--noconfirm',
        '--upx-dir=%s' % (UPX_PATH),
        '--log-level=WARN',
        '--onefile',
        '--name=Manager',
        '--icon=manager.ico',
        '--add-data=%s\\data\\pcsx2reg.txt;data' % (CWD),
        '--add-data=%s\\data\\pcsx2ui.txt;data' % (CWD),
        "Manager\\main.py",
    ])
