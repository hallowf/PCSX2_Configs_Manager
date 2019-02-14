import os, sys, configparser, argparse, subprocess



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
    On initialization provide game name and option
    option can be add or manage
    """
    def __init__(self, name, option):
        super(GameManager, self).__init__()
        self.name = name
        self.option = option

    def set_envs(self,env_dict):
        sys.stdout.write("Setting environment variables\n")
        env_dict["PCSX_SHARED_DIR"] = env_dict["PCSX_SHARED_DIR"].replace("\\", "\\\\")
        os.environ["PCSX_MAIN_EXE"] = env_dict["PCSX_BASE_DIR"] + "\\pcsx2.exe"
        for var in env_dict:
            if " " in env_dict[var]:
                env_dict[var] = "\"{}\"".format(env_dict[var])
            if var == "SHARED_MEMCARDS_FOLDER" and env_dict["_SHAREMEMCARDS"] == "no":
                sys.stdout.write("Memory cards not shared skipping variable\n")
                pass
            else:
                os.environ[var] = env_dict[var]

    def run_game_cmd(self):
        g_script = os.environ["PCSX_USER_CONFIGS"] + "\\Scripts\\games\\{}".format(self.name + ".cmd")
        emu_script = os.environ["PCSX_USER_CONFIGS"] + "\\Scripts\\pcsx2.bat"
        print(self.name)
        print(g_script)
        try:
            subprocess.call(g_script)
            try:
                subprocess.call(emu_script)
            except Exception as e:
                raise e
        except Exception as e:
            raise e





def add_args(parser):
    parser.add_argument("-cfg","--config", help="Configuration file", action="store")
    parser.add_argument("-option", help="(a|m|p) a for add game, m for manage, p for play", action="store", required=True)
    parser.add_argument("-game", help="Game name for running the scripts or creating a new one", action="store", required=True)
    parser.add_argument("-ac", "--auto_config", help="Automates creation of new game", action="store_true")
    args = parser.parse_args()
    if args.option == "m" or args.option == "p" and args.auto_config:
        parser.error("You can only use --auto_config when adding a new game")
    elif args.option == "p" and not args.config:
        parser.error("Missing config file can't set environment variables")
    return args






def run_main(args, config):
    g_manager = GameManager(args.game, args.option)
    if args.option == "p":
        env_dict = {x.upper():config["CONFIG"][x] for x in config["CONFIG"]}
        for var in env_dict:
            if env_dict[var] == "\"\"" or env_dict[var] == "" or env_dict[var] == " ":
                sys.stdout.write("Variable empty {}\n".format(var))
                # assert False
        g_manager.set_envs(env_dict)
        g_manager.run_game_cmd()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Manage PCSX2 configs')
    args = add_args(arg_parser)
    config = None
    if args.config:
        config = configparser.ConfigParser()
        config.read(args.config)
    run_main(args, config)
