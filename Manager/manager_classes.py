import os, shutil, sys, subprocess, winreg, ctypes

from manager_utils import get_manage_option

class GameManager(object):
    """
    On initialization provide game name, option, configparser and logging
    option can be auto_config manage or play
    if option is auto_config make sure the commands are run in order cf-at-rf-cc
    """
    def __init__(self, name, args, config, logger):
        super(GameManager, self).__init__()
        self.start_dir = sys._MEIPASS if getattr(sys, "frozen", False) else os.getcwd()
        self.data_dir = self.start_dir + "\\data"
        self.game_name = name
        self.option = args.option
        self.config = config
        self.logger = logger
        self.u_args = args
        self.c_data = {}
        self.game_preset = None
        self.curr_src_dir = None
        self.base_dir2 = None
        self.main_exe = None
        self.kdll = ctypes.windll.LoadLibrary("kernel32.dll")

    def __setitem__(self,k,v):
        self.c_data[k] = v

    def __getitem__(self,k):
        return self.c_data[k]

    # Set environment variables
    def set_self_values(self,env_dict):
        self.logger.info("Setting variables\n")
        env_dict["shared_dir"] = env_dict["shared_dir"].replace("\\", "\\\\")
        env_dict["shared_memcards_folder"] = env_dict["shared_memcards_folder"].replace("\\","\\\\")
        for v in env_dict:
            if " " in env_dict[v]:
                env_dict[v] = "\"%s\"" % (env_dict[v])
            if v == "shared_memcards_folder" and env_dict["share_memcards"] == "n":
                self.logger.info("Memory cards not shared skipping variable\n")
                pass
            else:
                if v == "base_dir":
                    self.base_dir2 = env_dict[v].replace("\\","\\\\")
                    self.main_exe = v + "\\pcsx2.exe"
                self.logger.debug("Setting %s to %s" % (v,env_dict[v]))
                self.__setitem__(v,env_dict[v])
        self.set_game_preset()

    # Sets self.game_preset to game preset folder
    def set_game_preset(self):
        game_preset = self.game_preset
        if not game_preset:
            game_preset = self.c_data['user_configs'] + "\\Games\\" + self.game_name
            self.game_preset = game_preset

    # Check if game has everything required to run
    def check_has_required(self):
        has_failed = False
        # Verify inside game preset
        game_preset = os.path.normpath(self.game_preset)
        required_dirs = ["inis", "shaders"]
        required_files = ["GameIndex.dbf", "pcsx2.exe"]
        game_f = [f for f in os.listdir(game_preset) if os.path.isfile("%s\\%s" % (game_preset,f))]
        game_d = [r_d for r_d in os.listdir(game_preset) if os.path.isdir("%s\\%s" % (game_preset,r_d))]
        for f in required_files:
            if f not in game_f:
                self.logger.error("Missing file %s\\%s" %(game_preset,f))
                has_failed = True
        for r_d in required_dirs:
            if r_d not in required_dirs:
                self.logger.error("Missing directory %s,%s" %(game_preset,r_d))
                has_failed = True
        return True if not has_failed else False

    # For copying files from PCSX_BASE_DIR to Game preset folder
    def recurse_copy(self, src, dest, ignore, w_over=False):
        ignored = False
        curr_src_dir = src if os.path.isdir(src) else self.curr_src_dir
        if curr_src_dir:
            self.curr_src_dir = curr_src_dir
            for fold in ignore:
                if curr_src_dir.endswith(fold):
                    self.logger.debug("Ignored " + curr_src_dir)
                    ignored = True
        if not ignored:
            if os.path.isdir(src):
                if not os.path.isdir(dest):
                    os.mkdir(dest)
                files = os.listdir(src)
                [self.recurse_copy(os.path.join(src, f),os.path.join(dest, f), ignore, w_over) for f in files]
            else:
                if w_over:
                    self.logger.debug("Overwriting " + src)
                    shutil.copyfile(src, dest)
                elif not os.path.isfile(dest) and not os.path.isdir(dest):
                    self.logger.debug("Copying " + src)
                    shutil.copyfile(src, dest)

    # For reading and writing files
    def read_write_file(self, file, mode, content=None):
        with open(file, mode) as f:
            if mode == "r":
                self.logger.debug("Reading : %s\n" % (file))
                content = f.read()
                return content
            elif mode == "w":
                if content:
                    self.logger.debug("Writing : %s\n" % (file))
                    f.write(content)

    # Copy templates to game folder
    def copy_templates(self):
        self.logger.info("Copying templates over to game folder\n")
        try:
            # pcsx2.reg script
            f_loc = "%s\\pcsx2.reg" % (self.game_preset)
            t_loc = "%s\\pcsx2reg.txt" % (self.data_dir)
            self.logger.info("Creating pcsx2.reg at: %s\n" % (f_loc))
            content = self.read_write_file(t_loc,"r")
            self.logger.debug("Replacing *BASE_DIR1* with %s" % (self.base_dir2))
            content = content.replace("*BASE_DIR1*", self.base_dir2)
            self.read_write_file(f_loc, "w", content)
            # PCSX2_ui.ini
            f_loc = f_loc.replace("pcsx2.reg", "inis\\PCSX2_ui.ini")
            t_loc = t_loc.replace("pcsx2reg.txt", "pcsx2ui.txt")
            self.logger.info("Creating PCSX2_ui.ini at: %s\n" % (f_loc))
            content = self.read_write_file(t_loc, "r")
            self.logger.debug("Replacing *BASE_DIR1* with %s" % (self.base_dir2))
            content = content.replace("*BASE_DIR1*", self.base_dir2)
            self.logger.debug("Replacing *BIOS* with %s" % (self.c_data['current_bios_name']))
            content = content.replace("*BIOS*", self.c_data['current_bios_name'])
            self.logger.debug("Replacing SHARED_DIR with %s" % (self.c_data['shared_dir']))
            content = content.replace("SHARED_DIR", self.c_data['shared_dir'])
            if self.config["MANAGER"]["replace_mem"] == "y":
                self.logger.debug("Replacing *MEMCARDS* with %s" % (self.c_data["shared_memcards_folder"]))
                content = content.replace("*MEMCARDS*", self.c_data["shared_memcards_folder"])
            else:
                content = content.replace("*MEMCARDS*", "memcards")
            self.read_write_file(f_loc, "w", content)
            return True
        except Exception as e:
            self.logger.error("Copying templates has failed\n")
            self.logger.debug(str(e))
            return False

    def manage_reg(self):
        self.logger.info("Editing registry values\n")
        root = winreg.HKEY_CURRENT_USER
        path = "Software\\PCSX2"
        to_replace = ["CustomDocumentsFolder", "SettingsFolder", "Install_Dir", "ThemesFolder"]
        for n in to_replace:
            value = self.base_dir2
            if n == "ThemesFolder":
                value = value + "\\themes"
            elif n == "SettingsFolder":
                value = value + "\\inis"
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                    self.logger.debug("Setting %s to %s" % (n, value))
                    winreg.SetValueEx(key, n, 0, winreg.REG_SZ, value)
            except Exception as e:
                self.logger.error("Failed to set registry values")
                self.logger.debug(str(e))

    def symlink_memcards(self, delete="n"):
        self.logger.info("Creating symlink for memcards\n")
        g_cards = self.game_preset + "\\memcards"
        s_cards = self.c_data["shared_memcards_folder"]
        cmd = "cmd /C mklink /J \"%s\" \"%s\"" % (g_cards, s_cards)
        if os.path.isdir(g_cards):
            delete = "y" if self.config["MANAGER"]["symlink_overwrite"] == "y" else input("Do you want to delete memcards folder if it exists(y|n):")
            if delete == "y":
                self.logger.info("WARNING: Deleting the memcards folder at: %s\n" % (g_cards))
                shutil.rmtree(g_cards)
        try:
            subprocess.call(cmd)
        except Exception as e:
            self.logger.error("Failed to create symlink")
            self.logger.debug(str(e))


    # For handling game management calls manage_game with action
    def handle_management(self, is_repeating=False):
        action = get_manage_option(is_repeating)
        was_success = self.manage_game(action)
        cont = self.config["MANAGER"]["continue"]
        # Loop for user input
        def ask_user(has_ran, cont):
            if was_success == True or was_success == False:
                cont = cont if cont else input("Continue(y|n):")
                if cont == "y":
                    is_repeating = True
                    self.handle_management(is_repeating)
                elif cont == "n":
                    sys.exit(0)
                else:
                    self.logger.info("Wrong value %s\n" % (cont))
                    retr = input("Retry(y|n):")
                    if retr == "y":
                        ask_user(was_success, cont)
                    else:
                        sys.exit(0)
            elif was_success == 0:
                self.logger.error("Invalid action " + action)
                is_repeating = True
                self.handle_management(is_repeating)
        ask_user(was_success, cont)

    ## Run the game must be called after set_envs
    def run_game_cmd(self):
        has_passed = self.check_has_required()
        use_gui = ""
        if self.config["MANAGER"]["interface"] == "n":
            use_gui = "--nogui"
        if has_passed:
            self.manage_reg()
            r_game = "%s\\pcsx2.exe %s\\%s.iso %s" % (self.game_preset, self.c_data['user_games'], self.game_name, use_gui)
            try:
                self.logger.info("Running cmd \"%s\"\n" % (r_game))
                subprocess.call(r_game)
                sys.exit(0)
            except Exception as e:
                self.logger.error("Cmd has failed %s" % (r_game))
                self.logger.debug(str(e))
        else:
            return False

    # Manage game
    def manage_game(self, action):

        # Manage functions
        # Calls self.recurse_copy
        def copy_f():
            u_conf = self.config["MANAGER"]["overwrite"]
            over_w = u_conf if u_conf == "y" else input("\nDo you want to overwrite files if they exist(y|n):")
            w_over = True if over_w == "y" else False
            self.logger.info("Copying Files\n")
            ignore = self.config["MANAGER"]["ignore"].split("\n")
            pcsx_dir = self.c_data['base_dir']
            game_preset = self.game_preset
            if os.path.isdir(pcsx_dir):
                if not os.path.isdir(os.path.abspath(game_preset)):
                    self.logger.debug("Game folder does not exist creating at " + game_preset)
                    os.mkdir(game_preset)
                self.recurse_copy(pcsx_dir, game_preset, ignore, w_over)
                if self.config["MANAGER"]["symlink"] == "y":
                    if self.config["MANAGER"]["replace_mem"] == "y":
                        self.logger.info("It seems that you have replace_mem=y,\n \
                        creating a symlink is useless\n \
                        since your pcsx2ui.ini will already contain the path to the shared cards folder\n")
                    self.symlink_memcards()
                return True
            else:
                self.logger.error("PCSX_BASE_DIR not set")
            return False

        def exit_n():
            sys.exit(0)

        funcs = {
            "cf" : copy_f,
            "at" : self.copy_templates,
            "pg" : self.run_game_cmd,
            "e" : exit_n,
        }

        try:
            return funcs[action]()
        except KeyError as e:
            return 0
