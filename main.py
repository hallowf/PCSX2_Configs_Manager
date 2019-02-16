import os, sys, configparser, argparse ,subprocess, traceback, shutil, logging, time

from manager_utils import get_manage_option, envs_to_dict, add_args
from manager_classes import GameManager

## main function
def run_main(args, config, logger):
    c_game = args.game if args.game else config["PLAY"]["game"]
    g_manager = GameManager(c_game, args, config, logger)
    env_dict = envs_to_dict(config, logger)
    g_manager.set_envs(env_dict)
    if args.option == "p":
        logger.info("Running game %s\n" % (c_game))
        time.sleep(1)
        g_manager.run_game_cmd()
    elif args.option == "ac":
        logger.info("Auto configuring %s\n" % (c_game))
        time.sleep(2)
        g_manager.manage_game("cf")
        g_manager.manage_game("at")
        g_manager.manage_game("rf")
        g_manager.manage_game("cc")
    elif args.option == "m":
        logger.info("Starting management\n")
        time.sleep(1)
        g_manager.handle_management()

## Configure and run
def startmain():
    sys.stdout.write("\n")
    arg_parser = argparse.ArgumentParser(description='Manage PCSX2 configs')
    args = add_args(arg_parser)
    di_level = "info" if not args.debug_level else args.debug_level
    d_level = None
    try:
        d_level = getattr(logging, di_level.upper())
    except Exception as e:
        sys.stdout.write("Invalid log level " + args.debug_level + "\n")
        sys.exit(1)
    if not isinstance(d_level, int):
        sys.stdout.write("Invalid log level " + di_level + "\n")
        sys.exit(1)
    logging.basicConfig(format="%(name)s: %(message)s",level=d_level)
    logger = logging.getLogger("PCSX2 Config Manager")
    config = configparser.ConfigParser()
    config.read(args.cfg)
    run_main(args, config, logger)

if __name__ == '__main__':
    startmain()
