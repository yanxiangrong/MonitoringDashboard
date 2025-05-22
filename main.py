import argparse
import tkinter as tk
from dashboard import MonitoringDashboardApp
from config import DEFAULT_EXPORTER_URL


def main():
    parser = argparse.ArgumentParser(description="Monitoring Dashboard")
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_EXPORTER_URL,
        help="Prometheus Exporter metrics URL (default: %(default)s)",
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Start in fullscreen mode",
    )
    args = parser.parse_args()

    root = tk.Tk()
    if args.fullscreen:
        root.attributes("-fullscreen", True)
    app = MonitoringDashboardApp(root, exporter_url=args.url)
    app.mainloop()


if __name__ == "__main__":
    main()
