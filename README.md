## Configuration
```
[PLAY]
game=Jak1 <= game name must match the iso's name EX: Jak.iso  = Jak

[CONFIG]
PCSX_BASE_DIR=R:\Emulators\PCSX\PCSX-DEV <= location of your pcsx installation
PCSX_USER_GAMES=R:\Emulators\PCSX\Games <= location of folder with isos
PCSX_SHARED_DIR=R:\Emulators\PCSX\Shared <= location of shared dir
PCSX_USER_CONFIGS=R:\Emulators\PCSX\Configs <= Location of game presets
_sharememcards=yes <= if you want to share memcards
SHARED_MEMCARDS_FOLDER=C:\users\user\Documents\pcsx2\memcards <= location of memcards folder
PCSX_CURRENT_BIOS_NAME=something.bin <= bios name *for replacing value in ui.ini
FART_EXE=R:\AnyFolder\Shared\fart.exe <= fart.exe full path

[MANAGER]
continue=y <= For managing game if y it will autocontinue if no will always stop after first cmd ran
ignore=bios <= folders to ignore
       memcards
```

## Usage

1. Place in config folder
2. Edit manager.ini
3. Run pcsx from it's installed location
4. Configure plugins accordingly
5. Run `Manager.exe -cfg manager.ini -option ac`
6. Play `Manager.exe -cfg manager.ini -option p`
3. run `Manager.exe --help` to see arguments

### Notes
**REQUIRES PYTHON 3.4^**
