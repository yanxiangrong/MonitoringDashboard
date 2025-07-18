import queue
import tkinter as tk

from .chart_manager import ChartManager
from .config_types import AppConfig
from .data_history import DataHistoryManager
from .logic.analyze import (
    CpuUsageAnalyzer,
    MemoryUsageAnalyzer,
    PhysicalDiskActiveTimeAnalyzer,
    MemoryCommitAnalyzer,
    NetworkSpeedAnalyzerV2,
    LogicalDiskSizeAnalyzer,
    GpuUsageAnalyzer,
)
from .logic.collect import RemoteMetricsCollector
from .logic.engine import MetricEngine
from .logic.metrics import update_metrics
from .menu import add_right_click_exit_menu


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk, app_config: AppConfig):
        self.root: tk.Tk = root
        self.q = queue.Queue()

        self.root.title(app_config.get("title", "Monitoring Dashboard"))
        self.w, self.h = 800, 480
        self.root.geometry(f"{self.w}x{self.h}")
        if app_config["fullscreen"]:
            root.attributes("-fullscreen", True)
            root.config(cursor="none")

        self.root.config(padx=2, pady=2)

        self.chart_manager = ChartManager(root)
        self.data_history = DataHistoryManager()
        add_right_click_exit_menu(self.root)

        self.engine = MetricEngine(
            interval=app_config["refresh_interval"],
            history_size=app_config["history_length"],
        )
        self.engine.register_collector(
            RemoteMetricsCollector(app_config["url"], app_config["fetch_timeout"])
        )
        self.engine.register_analyzer(CpuUsageAnalyzer())
        self.engine.register_analyzer(MemoryUsageAnalyzer())
        self.engine.register_analyzer(PhysicalDiskActiveTimeAnalyzer())
        self.engine.register_analyzer(NetworkSpeedAnalyzerV2())
        self.engine.register_analyzer(MemoryCommitAnalyzer())
        self.engine.register_analyzer(LogicalDiskSizeAnalyzer())
        self.engine.register_analyzer(GpuUsageAnalyzer())

        self.root.after_idle(self.check_queue)

        # 启动引擎
        self.engine.register_on_update(self.refresh_ui)
        self.engine.start()

    def refresh_ui(self):
        update_metrics(self)
        self.q.put("refresh")
        # self.root.after_idle(self.draw_charts)

    def check_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                if msg == "refresh":
                    self.root.after_idle(self.chart_manager.draw_charts)
        except queue.Empty:
            pass
        self.root.after(50, self.check_queue)

    def mainloop(self):
        self.root.mainloop()
        self.engine.stop()
