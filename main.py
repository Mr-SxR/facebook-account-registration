import os
import sys
import platform
import threading
from itertools import count
from concurrent.futures import ThreadPoolExecutor

if platform.system() == "Windows":
    os.system('')
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from ui.logo import logo
from ui.colors import GREEN, RED, WHITE, YELLOW, CYAN, EKL, LINE
from ui.display import print_lock
from core.device_manager import select_device, select_browser, select_server
from core.proxy_manager import get_proxy_list, create_proxy_cycle, get_no_proxy_data
from core.worker_manager import get_worker_count
from core.number_manager import process_file_input
from core.counter import Counter
from automation.create_task import create_worker


# Display current configuration state on screen
def render_config(config_state):
    logo()
    print(f" {GREEN}[{RED}●{GREEN}] Device Type  {EKL} {config_state.get('device', '...')}")
    print(f" {GREEN}[{RED}●{GREEN}] Browser      {EKL} {config_state.get('browser', '...')}")
    print(f" {GREEN}[{RED}●{GREEN}] Server       {EKL} {config_state.get('server', '...')}")
    print(f" {GREEN}[{RED}●{GREEN}] Proxy        {EKL} {config_state.get('proxy', '...')}")
    print(f" {GREEN}[{RED}●{GREEN}] Threads      {EKL} {config_state.get('workers', '...')}")
    print(f"{LINE}")


# Main entry point - collects user input and launches automation workers
def run_create():
    config_state = {}

    device_type = select_device(config_state, lambda: render_config(config_state))
    browser_type = select_browser(device_type, config_state, lambda: render_config(config_state))
    server = select_server(config_state, lambda: render_config(config_state))
    proxy_list = get_proxy_list(config_state, lambda: render_config(config_state))
    proxy_cycle = create_proxy_cycle(proxy_list)
    no_proxy_data = get_no_proxy_data()
    max_workers = get_worker_count(config_state, lambda: render_config(config_state))

    render_config(config_state)

    numbers = process_file_input()
    if numbers is None:
        input(f"\n {RED}Press Enter to exit...")
        return
    if not numbers:
        input(f"\n {RED}No numbers found. Press Enter to exit...")
        return

    render_config(config_state)
    input(f"\n {WHITE}Press Enter to start automation... ")

    logo()
    counter = Counter()

    config = {
        "device_type": device_type,
        "browser_type": browser_type,
        "server": server,
    }

    # Semaphore prevents excessive queuing beyond active workers
    sem = threading.Semaphore(max_workers + 5)
    wid_gen = count(1)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for num in numbers:
                sem.acquire()
                proxy_data = next(proxy_cycle) if proxy_cycle else no_proxy_data
                wid = next(wid_gen)
                future = executor.submit(create_worker, wid, num, proxy_data, config, counter)
                future.add_done_callback(lambda _: sem.release())
    except KeyboardInterrupt:
        print(f"\n\n {RED}Stopped by user.")

    # Print final summary
    with print_lock:
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()

        s = counter.summary()
        print(f"{LINE}")
        print(f" {GREEN}[{RED}●{GREEN}] {WHITE}Completed: {s['checked']} Numbers (Auto Create)")
        print(f" {GREEN}[{RED}●{GREEN}] {GREEN}Success: {s['success']}")
        print(f" {GREEN}[{RED}●{GREEN}] {YELLOW}Failed: {s['failed']}")
        print(f" {GREEN}[{RED}●{GREEN}] {RED}Error: {s['error']}")
        print(f" {GREEN}[{RED}●{GREEN}] {WHITE}No Account: {s['no_account']}")
        print(f"{LINE}")

    input(f"\n {WHITE}Press Enter to exit...")


if __name__ == '__main__':
    try:
        run_create()
    except KeyboardInterrupt:
        print(f"\n {RED}Cancelled.")
        sys.exit(0)
