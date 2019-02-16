import os, shutil, sys, subprocess

from manager_utils import get_manage_option

class GameManager(object):
    """
    On initialization provide game name, option, configparser and logging
    option can be auto_config manage or play
    if option is auto_config make sure the commands are run in order cf-at-rf-cc
    """
    def __init__(self, name, args, config, logger):
        super(GameManager, self).__init__()
        self.start_dir = os.getcwd()
        self.game_name = name
        self.option = args.option
        self.config = config
        self.logger = logger
        self.u_args = args
        self.game_preset = None
        self.curr_src_dir = None
        self.u_configs = None

    # Set environment variables
    def set_envs(self,env_dict):
        self.logger.info("Setting environment variables\n")
        env_dict["PCSX_SHARED_DIR"] = env_dict["PCSX_SHARED_DIR"].replace("\\", "\\\\")
        os.environ["PCSX_MAIN_EXE"] = env_dict["PCSX_BASE_DIR"] + "\\pcsx2.exe"
        self.u_configs = env_dict["PCSX_USER_CONFIGS"]
        for var in env_dict:
            if " " in env_dict[var]:
                env_dict[var] = "\"%s\"" % (env_dict[var])
            if var == "SHARED_MEMCARDS_FOLDER" and env_dict["_SHAREMEMCARDS"] == "no":
                self.logger.info("Memory cards not shared skipping variable")
                pass
            else:
                self.logger.debug("Setting %s to %s" % (var,env_dict[var]))
                os.environ[var] = env_dict[var]
        self.set_game_preset()

    # Sets self.game_preset to game preset folder
    def set_game_preset(self):
        game_preset = self.game_preset
        if not game_preset:
            game_preset = self.u_configs + "\\Games\\" + self.game_name
            self.game_preset = game_preset

    # Check if game has everything required to run
    def check_has_required(self):
        has_failed = False

        # Verify inside game preset
        game_preset = os.path.normpath(self.game_preset)
        required_dirs = ["inis", "shaders"]
        required_files = ["GameIndex.dbf", "pcsx2.exe", "pcsx2.reg"]
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
        # Verify cmd script
        r_cmd = "%s\\Scripts\\games\\%s.cmd" % (self.u_configs,self.game_name)
        if not os.path.isfile(r_cmd):
            self.logger.error("Missing cmd file %s" % (r_cmd))
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
                self.logger.debug("\nReading : %s\n" % (file))
                content = f.read()
                return content
            elif mode == "w":
                if content:
                    self.logger.debug("\nWriting : %s\n" % (file))
                    f.write(content)


    # Copy templates to game folder
    def copy_templates(self, src, dest):
        dest = dest.replace(".template", "") if dest.endswith(".template") else dest
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.mkdir(dest)
            files = os.listdir(src)
            [self.copy_templates(os.path.join(src, f),os.path.join(dest, f)) for f in files]
        else:
            if os.path.isfile(dest):
                self.logger.debug("Removing " + dest)
                os.remove(dest)
            self.logger.debug("Copying " + src)
            shutil.copyfile(src, dest)


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
                    self.logger.info("Wrong value " + cont)
                    retr = input("Retry(y|n):")
                    if retr:
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
        if has_passed:
            g_script = "%s\\Scripts\\games\\%s.cmd" % (self.u_configs, self.game_name)
            emu_script = self.u_configs + "\\Scripts\\pcsx2.bat"
            to_cmd = "%s && %s" % (g_script, emu_script)
            try:
                self.logger.info("Running cmd \"%s\"\n" % (to_cmd))
                subprocess.call(to_cmd)
            except Exception as e:
                self.logger.critical("Cmd has failed %s" % (to_cmd))
                sys.exit(1)
        else:
            sys.exit(1)
        sys.exit(0)


    # Manage game
    def manage_game(self, action):

        # Manage functions

        # Calls self.recurse_copy
        def copy_f():
            over_w = input("\nDo you want to overwrite files if they exist(y|n):")
            w_over = True if over_w == "y" else False
            self.logger.info("Copying Files\n")
            ignore = self.config["MANAGER"]["ignore"].split("\n")
            pcsx_dir = os.environ["PCSX_BASE_DIR"]
            game_preset = self.game_preset
            if os.path.isdir(pcsx_dir):
                if not os.path.isdir(os.path.abspath(game_preset)):
                    self.logger.debug("Game folder does not exist creating at " + game_preset)
                    os.mkdir(game_preset)
                self.recurse_copy(pcsx_dir, game_preset, ignore, w_over)
                return True
            else:
                self.logger.error("PCSX_BASE_DIR not set")
            return False

        # Add templates
        def add_t():
            self.logger.info("Copying templates\n")
            temp_loc = self.u_configs + "\\templates"
            game_preset = self.game_preset
            if os.path.isdir(temp_loc):
                if not os.path.isdir(game_preset):
                    self.logger.debug("Game folder does not exist creating at " + game_preset)
                    os.mkdir(game_preset)
                self.logger.info("Copying templates from %s to %s\n" % (temp_loc,game_preset))
                self.copy_templates(temp_loc, game_preset)
                return True
            else:
                self.logger.error("Templates not found")
            return False

        # For adding the game.cmd file
        def create_c():
            self.logger.info("Creating %s.cmd\n" % (self.game_name))
            temp_loc = self.u_configs + "\\Scripts\\games\\game.cmd.template"
            if os.path.isfile(temp_loc):
                temp_dest = temp_loc.replace("game.cmd.template", "%s.cmd" %(self.game_name))
                content = self.read_write_file(temp_loc, "r")
                content = content.replace("*game*", self.game_name)
                content = self.read_write_file(temp_dest, "w", content)
                return True
            else:
                self.logger.error("Can't find %s" % (temp_loc))
            return False

        # Run fart.bat
        def run_f():
            self.logger.info("Running fart\n")
            os.chdir(self.game_preset)
            try:
                subprocess.call("fart.bat")
                os.chdir(self.start_dir)
                return True
            except Exception:
                self.logger.error("Invalid path: %s\\fart.bat" % (self.game_preset))
            os.chdir(self.start_dir)
            return False

        def exit_n():
            sys.exit(0)

        funcs = {
            "cf" : copy_f,
            "at" : add_t,
            "rf" : run_f,
            "cc" : create_c,
            "pg" : self.run_game_cmd,
            "e" : exit_n,
        }

        try:
            return funcs[action]()
        except KeyError as e:
            return 0
