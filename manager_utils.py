import sys

## Get user input for action to manage game
def get_manage_option(again=False):
    if not again:
        sys.stdout.write("\nSelect the actions by order if creating a new game\n")
    sys.stdout.write("\n")
    sys.stdout.write("cf : Copy files from pcsx folder to game dir\n")
    sys.stdout.write("at : Add templates to game dir, rename them, and replace values\n")
    sys.stdout.write("cc : Create game.cmd file\n")
    sys.stdout.write("pg : Play game\n")
    sys.stdout.write("e : exit\n")
    sys.stdout.write("\n")
    action = input("Please select an option(cf|at|rf|cc|pg|e):")
    return action

## Return environment variables dict
def envs_to_dict(config, logger):
    env_dict = {x.upper():config["CONFIG"][x] for x in config["CONFIG"]}
    for var in env_dict:
        if env_dict[var] == "\"\"" or env_dict[var] == "" or env_dict[var] == " ":
            logger.warning("Variable empty %s" % (var))
    return env_dict

## Add arguments to parser and return them
def add_args(parser):
    ## Add group
    required_g = parser.add_argument_group("Required args")
    # required
    required_g.add_argument("-cfg", help="Configuration file", action="store", required=True)
    required_g.add_argument("-option", help="(ac|m|p) a for auto create game, m for manage, p for play", action="store", required=True)
    # optional
    parser.add_argument("-debug", "--debug_level", help="Set debug level", action="store")
    parser.add_argument("--game", help="Game name for running the scripts or creating a new one, can be set in manager.ini", action="store")
    args = parser.parse_args()
    return args
