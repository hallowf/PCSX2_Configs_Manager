import os, sys, configparser, argparse ,subprocess, traceback, shutil, logging



class F_Handler(object):
  """File handler usage: with F_Handler("file_name") as f: etc...."""
  def __init__(self, f_name , mode):
    super(F_Handler, self).__init__()
    self.name = f_name
    self.mode = mode

  def __enter__(self):
    self.file = open(self.name, self.mode)
    return self.file

  def __exit__(self, type, value, trace):
    if value:
      traceback.print_tb(trace)
    self.file.close()


class GameManager(object):
    """
    On initialization provide game name, option, configparser and logging
    option can be add, manage or play
    # TODO: use_autoconfig does not exist yet
    if option is 'add' use_autoconfig() can help autoconfigure the game
    based on the environment variables provided in config
    """
    def __init__(self, name, option, config, logger):
        super(GameManager, self).__init__()
        self.name = name
        self.option = option
        self.config = config
        self.logger = logger
        self.game_preset = None
        self.curr_src_dir = None

    # Set environment variables
    def set_envs(self,env_dict):
        self.logger.info("Setting environment variables\n")
        env_dict["PCSX_SHARED_DIR"] = env_dict["PCSX_SHARED_DIR"].replace("\\", "\\\\")
        os.environ["PCSX_MAIN_EXE"] = env_dict["PCSX_BASE_DIR"] + "\\pcsx2.exe"
        for var in env_dict:
            if " " in env_dict[var]:
                env_dict[var] = "\"{}\"".format(env_dict[var])
            if var == "SHARED_MEMCARDS_FOLDER" and env_dict["_SHAREMEMCARDS"] == "no":
                self.logger.info("Memory cards not shared skipping variable")
                pass
            else:
                self.logger.debug("Setting {} to {}".format(var, env_dict[var]))
                os.environ[var] = env_dict[var]

    # For copying files from PCSX_BASE_DIR to Game preset folder
    def recurse_copy(self, src, dest, ignore):
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
                [self.recurse_copy(os.path.join(src, f),os.path.join(dest, f), ignore) for f in files]
            else:
                if not os.path.isfile(dest) and not os.path.isdir(dest):
                    self.logger.debug("Copying " + src)
                    shutil.copyfile(src, dest)

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


    # Manage game
    def manage_game(self, action):

        # Manage functions

        # Calls self.recurse_copy
        def copy_f():
            ignore = self.config["COPY"]["ignore"].split("\n")
            pcsx_dir = os.environ["PCSX_BASE_DIR"]
            game_preset = os.environ["PCSX_USER_CONFIGS"] + "\\Games\\" + self.name
            self.game_preset = game_preset
            if os.path.isdir(pcsx_dir):
                if not os.path.isdir(os.path.abspath(game_preset)):
                    self.logger.debug("Game folder does not exist creating at " + game_preset)
                    os.mkdir(game_preset)
                self.recurse_copy(pcsx_dir, game_preset, ignore)
                return True
            else:
                self.logger.error("PCSX_BASE_DIR not set")
            return False

        def add_t():
            self.logger.info("Copying templates\n")
            temp_loc = os.environ["PCSX_USER_CONFIGS"] + "\\templates"
            game_preset = self.game_preset
            if not game_preset:
              game_preset = os.environ["PCSX_USER_CONFIGS"] + "\\Games\\" + self.name
              self.game_preset = game_preset
            if os.path.isdir(temp_loc):
                if not os.path.isdir(game_preset):
                    self.logger.debug("Game folder does not exist creating at " + game_preset)
                    os.mkdir(game_preset)
                self.logger.info("Copying templates from {} to {}\n".format(temp_loc, game_preset))
                self.copy_templates(temp_loc, game_preset)
                return True
            else:
                self.logger.error("Templates not found")
            return False

        def run_f():
            print(action)
            return True

        funcs = {
            "cf" : copy_f,
            "t" : add_t,
            "f" : run_f,
        }

        return funcs[action]()


    ## Run the game must be called after set_envs
    def run_game_cmd(self):
        g_script = r"{}\Scripts\games\{}".format(os.environ["PCSX_USER_CONFIGS"], self.name + ".cmd")
        emu_script = os.environ["PCSX_USER_CONFIGS"] + "\\Scripts\\pcsx2.bat"
        try:
            self.logger.info("Running cmd \"{} && {}\"".format(g_script, emu_script))
            subprocess.call([g_script, "&&", emu_script])
        except Exception as e:
            self.logger.critical("Cmd has failed")
            raise e





def template_copy(dest):
    if not os.path.isfile(dest):
        print("File not found")


## Add arguments to parser check and return them
def add_args(parser):
    parser.add_argument("-cfg", help="Configuration file", action="store", required=True)
    parser.add_argument("-option", help="(a|m|p) a for add game, m for manage, p for play", action="store", required=True)
    parser.add_argument("-game", help="Game name for running the scripts or creating a new one", action="store", required=True)
    parser.add_argument("-ac", "--auto_config", help="Automates creation of new game", action="store_true")
    parser.add_argument("-debug", "--debug_level", help="Set debug level", action="store")
    args = parser.parse_args()
    if (args.option == "m" or args.option == "p") and args.auto_config:
        sys.stdout.write("You can only use --auto_config when adding a new game\n")
    return args


## Return environment variables dict
def envs_to_dict(config, logger):
    env_dict = {x.upper():config["CONFIG"][x] for x in config["CONFIG"]}
    for var in env_dict:
        if env_dict[var] == "\"\"" or env_dict[var] == "" or env_dict[var] == " ":
            logger.warning("Variable empty {}".format(var))
    return env_dict


## Get user input for action to manage game
def get_manage_option():
    sys.stdout.write("Please select one option\n")
    sys.stdout.write("\n")
    sys.stdout.write("cf : Copy files from pcsx folder to game dir\n")
    sys.stdout.write("t : Add templates to game dir and rename them\n")
    sys.stdout.write("f : run fart.bat it requires fart.exe in game folder\n")
    sys.stdout.write("\n")
    action = input("Please select an option(cf|t|f):")
    return action



## main function
def run_main(args, config, logger):
    g_manager = GameManager(args.game, args.option, config, logger)
    env_dict = envs_to_dict(config, logger)
    g_manager.set_envs(env_dict)
    if args.option == "p":
        g_manager.run_game_cmd()
    elif args.option == "a":
        sys.stdout.write("Not implemented yet\n")
    elif args.option == "m":
        action = get_manage_option()
        has_ran = g_manager.manage_game(action)
        if has_ran:
            print("continue")
        else:
            print("Retry or try other?")


## Configure and run
def startmain():
    arg_parser = argparse.ArgumentParser(description='Manage PCSX2 configs')
    args = add_args(arg_parser)
    di_level = "info" if not args.debug_level else args.debug_level
    d_level = None
    try:
        d_level = getattr(logging, di_level.upper())
    except Exception as e:
        sys.stdout.write("Invalid log level " + args.debug_level + "\n")
        raise e
    if not isinstance(d_level, int):
        raise ValueError("Invalid log level " + di_level + "\n")
    logging.basicConfig(format="%(name)s: %(message)s",level=d_level)
    logger = logging.getLogger("PCSX2 Config Manager")
    config = configparser.ConfigParser()
    config.read(args.cfg)
    run_main(args, config, logger)

if __name__ == '__main__':
    startmain()
