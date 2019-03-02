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

# For Initializing the game and then try to resume state
def state_runner(logger, slot, wait_t):
    # string for slot regex
    slot_re = "Slot %s - .*" % (slot)
    t_wait_t = wait_t
    wait_t //= 2
    # Define app and connect
    logger.info("Connecting to app\n")
    app = Application(backend="uia").connect(title_re="PCSX2 .*", found_index=0)
    # Select main window
    app_window = app.window(title_re="PCSX2 .*")
    sys_menu_item = app_window[u"SystemMenuItem"]
    # Click system menu
    logger.info("Opening system menu\n")
    sys_menu_item.click_input()
    sys_child = app_window.child_window(title_re="System", control_type="Menu", found_index=0)
    # Select boot button trough new child window after selecting menu
    logger.info("Booting game to load stuff\n")
    boot = sys_child.child_window(title="Boot ISO (fast)", control_type="MenuItem")
    boot.click_input()
    # Wait a bit for the window to load
    logger.info("Waiting %s seconds for game to load\n" % (t_wait_t))
    time.sleep(wait_t)
    # Select game window
    game_window = app.window(title_re="Slot: .*")
    # Wait a bit for game to load and close window
    time.sleep(wait_t)
    logger.info("Closing game window\n")
    game_window.close()
    # Open system menu again
    logger.info("Reopening menus to load state\n")
    sys_menu_item.click_input()
    # Select and click load state menus
    load_state = sys_child.child_window(title_re="Load state\s.*", control_type="MenuItem")
    load_state.click_input()
    # Select state button and click it
    load_state_child = app_window.child_window(title_re="Load state\s.*", control_type="Menu", found_index=0)
    l_state_btn = load_state_child.child_window(title_re=slot_re, control_type="MenuItem")
    logger.info("Loading state\n")
    l_state_btn.click_input()
    logger.info("Done, exiting cli\n")
    sys.exit(0)
