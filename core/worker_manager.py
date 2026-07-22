from ui.colors import GREEN, RED, WHITE, EKL
from core.settings_manager import load_settings

MAX_SAFE_WORKERS = 200


# Prompt user for thread/worker count or use default from settings
def get_worker_count(config_state=None, render_callback=None):
    settings = load_settings()
    worker_cfg = settings.get("worker_settings", {})
    ask_worker = worker_cfg.get("ask_for_workers", True)
    default_raw = worker_cfg.get("default_workers", 30)

    try:
        default = int(default_raw)
    except (ValueError, TypeError):
        print(f"{RED} [!] Invalid 'default_workers' in settings ({default_raw!r}). Using 30.")
        default = 30

    if not ask_worker:
        if config_state is not None:
            config_state["workers"] = f"{default} Workers (Settings)"
        if render_callback:
            render_callback()
        return default

    if render_callback:
        render_callback()

    for _ in range(2):
        try:
            w_input = input(f" {GREEN}[{RED}●{GREEN}] Enter Threads/Workers ({default} recommended) {EKL} ").strip()
            if not w_input:
                if config_state is not None:
                    config_state["workers"] = f"{default} Workers (Default)"
                if render_callback:
                    render_callback()
                return default
            count = int(w_input)
        except (ValueError, TypeError):
            print(f"{RED} [!] Invalid input — please enter a number.")
            continue

        if count < 1:
            print(f"{RED} [!] Workers must be at least 1.")
            continue

        if count <= MAX_SAFE_WORKERS:
            if config_state is not None:
                config_state["workers"] = f"{count} Workers"
            if render_callback:
                render_callback()
            return count

        # Warn user about high worker counts that may crash low-end systems
        confirm = input(f"{RED} {count} workers may crash low-end PCs! Continue? (y/N) {EKL} ").strip().lower()
        if confirm in ("y", "yes"):
            if config_state is not None:
                config_state["workers"] = f"{count} Workers"
            if render_callback:
                render_callback()
            return count

    if config_state is not None:
        config_state["workers"] = f"{default} Workers (Default)"
    if render_callback:
        render_callback()
    return default
