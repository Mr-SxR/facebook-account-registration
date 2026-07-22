# ANSI color codes for terminal output
WHITE = "\033[1;97m"
GREEN = "\033[1;92m"
RED = "\033[1;91m"
DARK_GREEN = "\033[1;32m"
LIGHT_GRAY = "\033[1;37m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
BLUE = "\033[1;94m"
MAGENTA = "\033[1;95m"
ORANGE = "\x1b[38;5;208m"
GOLD = "\x1b[38;5;220m"
VIOLET = "\x1b[38;5;141m"
TOXIC = "\033[38;2;170;200;0m"
PURPLE = "\033[38;2;150;80;200m"
RESET = "\033[0m"

# Reusable UI elements
LINE = f"{CYAN}•{'━' * 47}•"
EKL = f"{CYAN}:{WHITE}"


# Format a menu option number with colored brackets
def opt(num):
    return f"{GREEN}[{RED}{str(num).zfill(2)}{GREEN}]"
