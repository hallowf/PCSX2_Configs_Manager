import PyInstaller.__main__
import os, shutil

UPX_PATH = os.environ["UPX_PATH"]
CWD = os.path.dirname(os.path.abspath(__file__))


PyInstaller.__main__.run([
        '--noconfirm',
        '--upx-dir=%s' % (UPX_PATH),
        '--log-level=WARN',
        '--onefile',
        '--name=Manager',
        '--icon=manager.ico',
        '--add-data=%s\\data\\pcsx2ui.txt;data' % (CWD),
        "Manager\\main.py",
    ])


# Add other to dist
to_add = {
    "manager.ini.template": "Manager\\manager.ini.template",
}
t_dest = "%s\\dist\\" % (CWD)

for f in to_add:
    f_src = "%s\\%s" % (CWD, to_add[f])
    f_dest = t_dest + f
    shutil.copyfile(f_src, f_dest)
