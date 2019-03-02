import os, shutil, sys, subprocess, winreg, time

from manager_utils import get_manage_option

class GameManager(object):
    """
    On initialization provide game name, args, configparser and logging
    option can be ac m or p (auto configure, manage, play)
    if option is ac (auto configuration) make sure the commands are run in order cf-at
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
        self.r_proc = None
        self.loaded_state = None

    def __setitem__(self,k,v):
        self.c_data[k] = v

    def __getitem__(self,k):
        return self.c_data[k]

    # Set environment variables
    def set_self_values(self,env_dict):
        self.logger.info("Setting variables\n")
        for n in env_dict:
            v = env_dict[n]
            if " " in env_dict[n]:
                env_dict[n] = "\"%s\"" % (env_dict[n])
            if n == "shared_memcards_folder" and env_dict["share_memcards"] == "n":
                self.logger.info("Memory cards not shared skipping variable\n")
                pass
            else:
                if n == "base_dir":
                    self.base_dir2 = env_dict[n].replace("\\","\\\\")
                    self.main_exe = env_dict[n] + "\\pcsx2.exe"
                elif n == "shared_dir" or n == "shared_memcards_folder":
                    v = env_dict[n].replace("\\","\\\\")
                self.logger.debug("Setting %s to %s" % (n,v))
                self.__setitem__(n,v)
        self.set_game_preset()

    # Sets self.game_preset to game preset folder
    def set_game_preset(self):
        game_preset = self.game_preset
        if not game_preset:
            game_preset = self.c_data['user_configs'] + "\\Games\\" + self.game_name
            self.game_preset = game_preset

    # Check if game has everything required to run
    def check_has_required(self):
        self.logger.info("Checking requirements before starting game\n")
        has_failed = False
        game_preset = os.path.normpath(self.game_preset)
        g_iso = "%s\\%s.iso" % (self.c_data['user_games'], self.game_name)
        if not os.path.isfile(g_iso):
            self.logger.error("Couldn't find game iso at: %s" % (g_iso))
            has_failed = True
        if not os.path.isdir(game_preset):
            self.logger.error("Couldn't find game preset folder at: %s" % (game_preset))
            has_failed = True
        # Verify inside game preset
        required_dirs = ["inis", "shaders"]
        required_files = ["GameIndex.dbf", "pcsx2.exe"]
        if not has_failed:
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
        # # TODO: This might catch all subfolders but does not catch the main root
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
                l_dir = os.listdir(src)
                [self.recurse_copy(os.path.join(src, i),os.path.join(dest, i), ignore, w_over) for i in l_dir]
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
            # PCSX2_ui.ini
            f_loc = "%s\\inis\\PCSX2_ui.ini" % (self.game_preset)
            t_loc = "%s\\pcsx2ui.txt" % (self.data_dir)
            self.logger.info("Creating PCSX2_ui.ini at: %s\n" % (f_loc))
            content = self.read_write_file(t_loc, "r")
            self.logger.debug("Replacing *BASE_DIR1* with %s" % (self.base_dir2))
            content = content.replace("*BASE_DIR1*", self.base_dir2)
            self.logger.debug("Adding game iso to CurrentIso")
            content = content.replace("*CURRENT_ISO*", "%s\\\\%s.iso" % (self.c_data["user_games"].replace("\\","\\\\"), self.game_name))
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
            delete = "y" if self.config["MANAGER"]["symlink_overwrite"] == "y" else input("\nDo you want to delete memcards folder if it exists(y|n):")
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
                cont = cont if cont else input("\nContinue(y|n):")
                if cont == "y":
                    is_repeating = True
                    self.handle_management(is_repeating)
                elif cont == "n":
                    sys.exit(0)
                else:
                    self.logger.info("Wrong value %s\n" % (cont))
                    retr = input("\nRetry(y|n):")
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
            r_cmd = None
            if self.u_args.resume:
                r_cmd = "%s\\pcsx2.exe" % (self.game_preset)
            else:
                r_cmd = "%s\\pcsx2.exe %s\\%s.iso %s" % (self.game_preset, self.c_data['user_games'], self.game_name, use_gui)
            try:
                self.logger.info("Running cmd \"%s\"\n" % (r_cmd))
                self.r_proc = subprocess.Popen(r_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                time.sleep(2)
                self.logger.debug("Launch successfull")
                return True
            except Exception as e:
                self.logger.error("Cmd has failed %s" % (r_cmd))
                self.logger.debug(str(e))
        else:
            return False

    # Manage game
    def manage_game(self, action):

        # Manage functions
        # Calls self.recurse_copy
        def copy_f():
            self.logger.info("Copying Files\n")
            u_conf = self.config["MANAGER"]["overwrite"]
            over_w = u_conf if u_conf == "y" else input("\nDo you want to overwrite files if they exist(y|n):")
            w_over = True if over_w == "y" else False
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
                if self.config["MANAGER"]["custom_inis"] == "y":
                    g_inis = "%s\\%s" % (self.config["MANAGER"]["custom_inis_folder"], self.game_name)
                    self.logger.info("Copying custom inis from %s\n" % (g_inis))
                    w_over = True
                    self.recurse_copy(g_inis, game_preset, ignore, w_over)
                return True
            else:
                self.logger.error("PCSX_BASE_DIR not set")
            return False

        def exit_n():
            sys.exit(0)

        funcs = {
            "cf" : copy_f,
            "at" : self.copy_templates,
            "sm" : self.symlink_memcards,
            "pg" : self.run_game_cmd,
            "e" : exit_n,
        }

        try:
            return funcs[action]()
        except KeyError as e:
            return 0
