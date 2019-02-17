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

First donwload the [exe](https://github.com/hallowf/PCSX2_Configs_Manager/releases) place it near your pcsx desired configs location
and make a file named manager.ini you can name it whatever you want copy the contents from [Configuration](#configuration)
replacing everything with your own values:


To configure a game
1. Run pcsx from it's installed location
2. Configure plugins and settings accordingly
3. Replace game name in manager.ini or specify it as an argument
4. Run `Manager.exe -cfg manager.ini -option ac`
5. Play `Manager.exe -cfg manager.ini -option p`
6. run `Manager.exe --help` to see arguments

#### Dev
**REQUIRES PYTHON 3.7^**
Windows:

```
cd AnyFolder

git clone https://github.com/hallowf/PCSX2_Configs_Manager Manager

# Configuring virtual environment

py -3.7 -m pip install virtualenv

py -3.7 -m virtualenv venv

venv\Scripts\activate

pip install -r requirements.txt

python main.py --help


# Building

pyinstaller main.py

# Configure main.spec

pyinstaller --onefile main.spec

```

Or just download it as a zip, create the folder Configs and copy the contents of the zip inside
and then all configure the virtual environment

## iDEAS NOT YET IMPLEMENTED

1. Multiple game automatic configuration
* for this I will need a "custom" inis folder, and a setting for selecting custom inis or not,
in case there is a need to create equal configurations for multiple games

2. Add setting to automatic overwrite files when copying in manager.ini and maybe as an optional argument too

3. Fix the issue with lack of permission to create a hard symlink
* using --uac-admin with pyinstaller didn't seem to work (*Might be due to travis preview support on windows environments*)

4. Backup memorycards
* This might require a lot of code if using connections to cloud providers
* I might just make an archive out of them
* [dropbox](https://github.com/dropbox/dropbox-sdk-python) is nice and easy
* Mega there seems to be no current updated wrapper
* [GoogleDrive](https://developers.google.com/drive/api/v3/quickstart/python) shouldn't be so complicated
* Microsoft [OneDrive](https://github.com/OneDrive/onedrive-sdk-python) shouldn't be that hard too
* It would also be nice to have a "history system" implemented maybe I can leave in the manager.ini a value
for how many copys to keep in the cloud before starting to delete old ones,
however going to the trouble of renaming files already stored makes no sense,
so maybe attach to the zip name a simple timestamp that I could read with python's
datetime module
