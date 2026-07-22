import sys
import threading
from ui.display import safe_print, status_line, print_lock
from ui.colors import WHITE


# Thread-safe counter for tracking automation results across all workers
class Counter:
    def __init__(self):
        self._lock = threading.Lock()
        self.checked = 0
        self.success = 0
        self.failed = 0
        self.error = 0
        self.no_account = 0

    # Increment the appropriate counter and print status update
    def update(self, status, number=None, message=None, color=None):
        with self._lock:
            if status == "success":
                self.success += 1
            elif status == "failed":
                self.failed += 1
            elif status == "error":
                self.error += 1
            elif status == "no_account":
                self.no_account += 1
            self.checked += 1
            checked, success, failed, error, no_account = (
                self.checked, self.success, self.failed, self.error, self.no_account
            )

        if message and number:
            c = color or WHITE
            safe_print(f"{c} {message} {number}", checked, success, failed, error, no_account)
        elif message:
            c = color or WHITE
            safe_print(f"{c} {message}", checked, success, failed, error, no_account)
        else:
            with print_lock:
                sys.stdout.write(status_line(checked, success, failed, error, no_account))
                sys.stdout.flush()

    # Reset all counters to zero
    def reset(self):
        with self._lock:
            self.checked = 0
            self.success = 0
            self.failed = 0
            self.error = 0
            self.no_account = 0

    # Return current counts as a dictionary
    def summary(self):
        return {
            "checked": self.checked,
            "success": self.success,
            "failed": self.failed,
            "error": self.error,
            "no_account": self.no_account,
        }
