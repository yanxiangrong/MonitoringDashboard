import argparse
import tkinter as tk
from typing import cast

import yaml

from app.config_types import AppConfig
from app.default_config import DEFAULT_CONFIG
from app.main_window import MonitoringDashboardApp


def load_config() -> AppConfig:
    config = cast(AppConfig, DEFAULT_CONFIG.copy())
    try:
        with open("config/config.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                config.update(data)
    except FileNotFoundError:
        pass

    parser = argparse.ArgumentParser(description="Monitoring Dashboard")
    parser.add_argument(
        "--url",
        type=str,
        default=config["url"],
        help="Prometheus Exporter metrics URL (default: %(default)s)",
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        default=config["fullscreen"],
        help="Start in fullscreen mode (default: %(default)s)",
    )
    args = parser.parse_args()
    config.update(vars(args))
    return config


def main():
    config = load_config()

    root = tk.Tk()

    app = MonitoringDashboardApp(root, config)
    app.mainloop()


if __name__ == "__main__":
    main()
