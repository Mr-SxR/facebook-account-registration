import os
import platform
from ui.colors import GREEN, CYAN, RED, ORANGE, LINE

VERSION = "1.0.0"


# Clear terminal screen (cross-platform)
def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


# Display the tool banner with ASCII art logo and info
def logo():
    clear()
    print(f"""{GREEN}
      .d8888.  db    db  d8888b.
      88'  YP  `8b  d8'  88  `8D
      `8bo.     `8bd8'   88oobY'
        `Y8b.   .dPYb.   88`8b
      db   8D  .8P  Y8.  88 `88.
      `8888Y'  YP    YP  88   YD   {ORANGE}V-{VERSION}
{LINE}
 {GREEN}[{RED}●{GREEN}] TOOL OWNER   {CYAN}:{GREEN} @mrsxrtool
 {GREEN}[{RED}●{GREEN}] TOOL         {CYAN}:{GREEN} AUTO CREATE
 {GREEN}[{RED}●{GREEN}] TOOL STATUS  {CYAN}:{GREEN} PAID
{LINE}""")
