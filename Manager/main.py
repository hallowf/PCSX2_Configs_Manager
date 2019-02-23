import os, sys, configparser, argparse ,subprocess, traceback, shutil, logging, time

from manager_utils import get_manage_option, envs_to_dict, add_args
from manager_classes import GameManager

## main function
def run_main(args, config, logger):
    c_game = args.game if args.game else config["PLAY"]["game"]
    if "\n" in c_game:
        c_game = c_game.split("\n")
    elif " " in  c_game:
        c_game = c_game.split(" ")
    env_dict = envs_to_dict(config, logger)
    if args.option == "mac":
        for game in c_game:
            g_manager = GameManager(game, args, config, logger)
            g_manager.set_self_values(env_dict)
            logger.info("Auto configuring %s\n" % (game))
            time.sleep(1)
            g_manager.manage_game("cf")
            g_manager.manage_game("at")
        logger.info("Finished configuring all games")
    else:
        if not isinstance(c_game, list):
            g_manager = GameManager(c_game, args, config, logger)
            g_manager.set_self_values(env_dict)
            if args.option == "p":
                logger.info("Running game %s\n" % (c_game))
                time.sleep(1)
                has_ran = g_manager.run_game_cmd()
                if has_ran:
                    sys.exit(0)
                else:
                    sys.exit(1)
            elif args.option == "ac":
                logger.info("Auto configuring %s\n" % (c_game))
                time.sleep(1)
                g_manager.manage_game("cf")
                g_manager.manage_game("at")
            elif args.option == "m":
                logger.info("Starting management\n")
                time.sleep(1)
                g_manager.handle_management()
        else:
            logger.error("It seems you have provided multiple game names, please use -option mac to configure them\n")
            logger.info("Games provided are %s" % (c_game))

## Configure and run
def start_main():
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
    start_main()
