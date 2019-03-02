# PCSX2_Configs_Manager
This is just a simple cli tool I wrote in python that allows you to easily configure pcsx2 plugins/settings accordingly to games it's really simple to use and configure and no longer requires [This scripts](https://github.com/hallowf/PCSX2_Configs)

## Configuration

```
[PLAY]
game=Jak1 <= game name must match the iso's name EX: Jak.iso  = Jak, can also be multiple values see ignore at the end

[CONFIG]
BASE_DIR=R:\Emulators\PCSX\PCSX-DEV <= location of your pcsx installation

USER_GAMES=R:\Emulators\PCSX\Games <= location of folder with isos

SHARED_DIR=R:\Emulators\PCSX\Shared <= location of shared dir (Contains your bios and plugins you can just copy them over)

USER_CONFIGS=R:\Emulators\PCSX\Configs <= Location of game presets (Place to save game configurations)

SHARE_MEMCARDS=y <= if you want to share memcards

SHARED_MEMCARDS_FOLDER=C:\users\user\Documents\pcsx2\memcards <= location of memcards folder

CURRENT_BIOS_NAME=something.bin <= bios name *for replacing value in ui.ini

[MANAGER]
interface=n <= Enables/Disables pcsx2 GUI

continue=y <= For managing game if y it will autocontinue if no will always stop after first cmd ran

overwrite=y <= If y, when copying files overwrite them else copy missing ones

replace_mem=y <= It will replace MemoryCards=*MEMCARDS* with your shared memcards folder if n it will replace *MEMCARDS* with memcards (Default location)

symlink=n <= Instead of replacing memorycards path this creates a symbolic link with your shared folder *(It's a shortcut basically)*

symlink_overwrite=n <= If set to y it will delete memcards (located at the new game config path) before trying to create a symlink

custom_inis=y <= Only for multiple game configuration, Use independent inis for each game

custom_inis_folder=R:\Emulators\PCSX\Custom_Inis <= Folder containing custom inis (*Inside it put a folder with the game's name and the inis folder inside*)

ignore=bios <= folders to ignore
       memcards <= indentation is important just press "tab" or "space" until they line up
```

## Features

1. Easy automatic configuration for games
2. Multiple game automatic configuration
 * Supports custom inis per game
3. Individual game management
  * If you prefer to manually configure each game
4. Completely independent
 * Before this used to depend on scripts now it's just a single executable and a configuration file
5. Resume states read [this](#resuming-state)

## Usage

First donwload the [exe](https://github.com/hallowf/PCSX2_Configs_Manager/releases) place it near your pcsx desired configs location and make a file named manager.ini you can name it whatever you want copy the contents from [Configuration](#configuration) replacing everything with your own values:

### Basic usage

To configure a game
1. Run pcsx2 from it's installed location
2. Configure plugins and settings accordingly
3. Replace game name in manager.ini or specify it as an argument
4. Run `Manager.exe -cfg manager.ini -option ac`
5. Play `Manager.exe -cfg manager.ini -option p`
6. Run `Manager.exe --help` to see arguments

### Multiple automatic configuration

To configure multiple game
1. Run pcsx2 from it's installed location
2. Configure plugins and settings accordingly
3. Create a folder with the game name in custom_inis_folder
4. Copy the inis folder from pcsx2 location to the folder you just created
5. Repeat steps above for desired games
6. Replace game name in manager.ini put all games you just configured
 * If you pass them as arguments put them inside quotes and with spaces in between EX: --game "Jak1 Jak2 Jak3"
7. Run `Manager.exe manager.ini mac`
8. Before playing remove all names in manager.ini except the one you want to play
9. Play `Manager.exe manager.ini p`


### Resuming state

This might lead to unexpected issues please use it carefully
1. `Manager.exe manager.ini p --resume 0`


**From the pcsx2 wiki:**

You should be safe if you normally boot games from the disc and load a memcard save, then proceed playing and using savestates from there, and quit the game after making a final memcard save. Relying on savestates to continue where you left off directly instead of loading from a memcard can lead to inconsistencies. Most of the time you should be okay but occasionally you can run into situations where the savestate insists you do not have a valid memcard save.
In case this happens, simply reboot the game and load from the memcard save normally, instead of directly loading from the savestate. Later savestates should remember that you started from a memcard save and will not repeat the problem.

### CLI

```
Manager.exe manager.ini p
|               |       |
Program       Config   Option
```

1. Option
 * p - Play
 * ac - Auto configuration
 * mac - Multiple auto configuration
 * m - Manage
2. Config - Configuration file
3. `--debug`
 * info - Default only shows info on execution
 * debug - Log everything
4. `--game`
 * Game or games to use (only specify multiple games for multiple auto configuration)
5. `--resume`
  * From 0 to 9 save state to resume
  * Use it only with option p
6. `--load_time`
  * Time to wait for game to run before trying to resume state
  * Default is 15

## DISCLAIMER:

This "product" is in no way associated with [PCSX2](https://pcsx2.net/), this is just something I built for learning mostly but also to automate what I consider a tedious process

## Dev
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

python pyinstaller.py

```

Or just download it as a zip, create the folder Configs and copy the contents of the zip inside
and then all configure the virtual environment

## iDEAS NOT YET IMPLEMENTED

1. Backup memorycards
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
