import sys, time
from pywinauto.application import Application

## Get user input for action to manage game
def get_manage_option(again=False):
    if not again:
        sys.stdout.write("\nSelect the actions by order if creating a new game\n")
        sys.stdout.write("Creating a symbolic link is unnecessary if you are replacing memory cards path in the config\n\n")
    sys.stdout.write("cf : Copy files from pcsx folder to game dir\n")
    sys.stdout.write("at : Add templates to game dir, rename them, and replace values\n")
    sys.stdout.write("sm : Creates a symbolic link to shared memcards\n")
    sys.stdout.write("pg : Play game\n")
    sys.stdout.write("e : exit\n")
    action = input("\nPlease select an option(cf|at|sm|pg|e):")
    sys.stdout.write("\n")
    return action

## Return environment variables dict
def envs_to_dict(config, logger):
    env_dict = {x.lower():config["CONFIG"][x] for x in config["CONFIG"]}
    for var in env_dict:
        if env_dict[var] == "\"\"" or env_dict[var] == "" or env_dict[var] == " ":
            logger.warning("Variable empty %s" % (var))
    return env_dict

## Add arguments to parser and return them
def add_args(parser):
    # required
    parser.add_argument("cfg", help="Configuration file", action="store")
    parser.add_argument("option", help="(ac|mac|m|p) ac for auto create game, mac for multiple auto creation, m for manage, p for play", action="store")
    # optional
    parser.add_argument("--debug", help="Set debug level", action="store")
    parser.add_argument("--game", help="Game name, can be set in manager.ini", action="store")
    parser.add_argument("--resume", help="Resume state (0 to 9)", action="store")
    parser.add_argument("--load_time", help="Time in seconds to wait while loading game when resuming state", action="store")
    args = parser.parse_args()
    games = None
    if args.game:
        games = args.game.split(" ") if " " in args.game else args.game
    # Check usage
    if args.resume and args.option != "p":
        sys.stdout.write("Found resume argument but invalid option %s\n" % (args.option))
        sys.stdout.write("You can't resume a state while managing or configuring game\n")
        sys.exit(1)
    elif args.option == "mac" and args.game and not isinstance(games, list):
        sys.stdout.write("You tried to configure multiple games but only provided one name: %s\n" % (games))
    # Check and set values
    if args.resume:
        try:
            state = int(args.resume)
            if state > 9:
                raise ValueError
            args.resume = state
        except ValueError as e:
            sys.stdout.write("--resume must be a number from 0 to 9, closing...\n")
            sys.exit(1)
    if args.load_time:
        try:
            wait_t = int(args.load_time)
            if wait_t < 10 or wait_t > 150:
                raise ValueError
        except ValueError as e:
            sys.stdout.write("--load_time must be a number from 10 to 150, setting to default: 15\n")
    return args
