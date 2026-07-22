import sys
import threading
from ui.colors import GREEN, WHITE, CYAN, YELLOW, RED

print_lock = threading.Lock()


# Build the live status bar string shown at the bottom of the terminal
def status_line(checked, success, failed, error, no_account=0):
    return (
        f"\r{GREEN}[{WHITE}Mr-SxR{GREEN}] "
        f"{WHITE}CHECKED:-{checked}{CYAN}|"
        f"{GREEN}SUCCESS:-{success}{CYAN}|"
        f"{YELLOW}FAILED:-{failed}{CYAN}|"
        f"{RED}ERROR:-{error}{CYAN}|"
        f"{WHITE}NO-ACC:-{no_account}"
    )


# Thread-safe print that clears the line, writes text, then restores the status bar
def safe_print(text, checked=0, success=0, failed=0, error=0, no_account=0):
    with print_lock:
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        try:
            sys.stdout.write(str(text) + '\n')
        except UnicodeEncodeError:
            sys.stdout.write(str(text).encode('utf-8', errors='ignore').decode('utf-8') + '\n')
        sys.stdout.write(status_line(checked, success, failed, error, no_account))
        sys.stdout.flush()
