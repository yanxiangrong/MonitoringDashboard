import tkinter as tk
from chart_widgets.time_series import TimeSeries
from metrics.analyze import (
    CpuUsageAnalyzer,
    MemoryUsageAnalyzer,
    PhysicalDiskActiveTimeAnalyzer,
    NetworkSpeedAnalyzer,
)
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine
from metrics.index import get_value_from_metric


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk, exporter_url: str):
        self.root: tk.Tk = root
        self.root.title("MonitoringDashboard")
        self.w, self.h = 600, 400
        self.root.geometry(f"{self.w}x{self.h}")
        self.root.config(padx=2, pady=2)

        self.cpu_chart = TimeSeries(root, outline="steelblue", title="CPU Usage")
        self.cpu_chart.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        self.memory_chart = TimeSeries(root, outline="slateblue", title="Memory Usage")
        self.memory_chart.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
        self.disk0_chart = TimeSeries(
            root, outline="forestgreen", title="Disk Active Time (Disk 0)"
        )
        self.disk0_chart.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        self.disk1_chart = TimeSeries(
            root, outline="forestgreen", title="Disk Active Time (Disk 1)"
        )
        self.disk1_chart.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")
        self.network_chart = TimeSeries(
            root, outline="saddlebrown", title="Network Speed", unit=" Mbps"
        )
        self.network_chart.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

        # 设置行和列的权重
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)

        self.engine = MetricEngine(interval=1, history_size=600)
        self.engine.register_collector(RemoteMetricsCollector(exporter_url))
        self.engine.register_analyzer(CpuUsageAnalyzer())
        self.engine.register_analyzer(MemoryUsageAnalyzer())
        self.engine.register_analyzer(PhysicalDiskActiveTimeAnalyzer())
        self.engine.register_analyzer(NetworkSpeedAnalyzer())

        # 用于保存历史数据，便于后续画图
        self.cpu_history: list[tuple[float, float]] = []
        self.memory_history: list[tuple[float, float]] = []
        self.disk0_history: list[tuple[float, float]] = []
        self.disk1_history: list[tuple[float, float]] = []
        self.network_history: list[tuple[float, float]] = []
        self.scrape_time = 0

        # 启动引擎
        self.engine.register_on_update(self.refresh_ui)
        self.engine.start()

    def update_metrics(self):
        scrape_time = self.engine.get_last_scrape_time()
        cpu_usage_metrics = self.engine.get_metric_range(
            "cpu_usage_percent", scrape_time - 61, scrape_time
        )
        memory_usage_metrics = self.engine.get_metric_range(
            "memory_usage_percent", scrape_time - 61, scrape_time
        )
        disk_usage_metrics = self.engine.get_metric_range(
            "disk_io_util_percent", scrape_time - 61, scrape_time
        )
        network_usage_metrics = self.engine.get_metric_range(
            "network_speed_mbps", scrape_time - 61, scrape_time
        )

        self.scrape_time = scrape_time
        self.cpu_history = get_value_from_metric(cpu_usage_metrics)
        self.cpu_chart.update_values(
            self.cpu_history, self.scrape_time - 60, self.scrape_time
        )
        self.memory_history = get_value_from_metric(memory_usage_metrics)
        self.memory_chart.update_values(
            self.memory_history, self.scrape_time - 60, self.scrape_time
        )
        self.disk0_history = get_value_from_metric(
            disk_usage_metrics, {"disk": "0"}
        )
        self.disk1_history = get_value_from_metric(
            disk_usage_metrics, {"disk": "1"}
        )
        self.disk0_chart.update_values(
            self.disk0_history, self.scrape_time - 60, self.scrape_time
        )
        self.disk1_chart.update_values(
            self.disk1_history, self.scrape_time - 60, self.scrape_time
        )
        self.network_history = get_value_from_metric(network_usage_metrics)
        self.network_chart.update_values(
            self.network_history, self.scrape_time - 60, self.scrape_time
        )

    def draw_charts(self):
        self.cpu_chart.draw_chart()
        self.memory_chart.draw_chart()
        self.disk0_chart.draw_chart()
        self.disk1_chart.draw_chart()
        self.network_chart.draw_chart()

    def refresh_ui(self):
        self.update_metrics()
        self.root.after_idle(self.draw_charts)

    def mainloop(self):
        self.root.mainloop()
        self.engine.stop()
