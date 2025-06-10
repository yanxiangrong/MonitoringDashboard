import queue
import tkinter as tk

from chart_widgets.chart import Chart, EmptyChart
from chart_widgets.heatmap import Heatmap
from chart_widgets.progress_bar import DiskProgressBars
from chart_widgets.time_series import TimeSeries
from metrics.analyze import (
    CpuUsageAnalyzer,
    MemoryUsageAnalyzer,
    PhysicalDiskActiveTimeAnalyzer,
    MemoryCommitAnalyzer,
    NetworkSpeedAnalyzerV2,
    LogicalDiskSizeAnalyzer,
    GpuUsageAnalyzer,
)
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine
from metrics.index import get_value_from_metric, get_value_from_metric_group_by


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk, exporter_url: str):
        self.root: tk.Tk = root
        self.q = queue.Queue()

        self.root.title("MonitoringDashboard")
        self.w, self.h = 600, 400
        self.root.geometry(f"{self.w}x{self.h}")
        self.root.config(padx=2, pady=2)

        self.add_right_click_exit_menu()

        self.chart_list: list[Chart] = []

        self.cpu_chart = TimeSeries(root, outline="steelblue", title="CPU Usage")
        self.add_chart(self.cpu_chart)
        self.cpu_heatmap_chart = Heatmap(root, title="CPUs Usage")
        self.add_chart(self.cpu_heatmap_chart)

        self.memory_chart = TimeSeries(root, outline="slateblue", title="Mem Usage")
        self.add_chart(self.memory_chart)
        self.memory_commit_chart = TimeSeries(
            root, outline="slateblue", title="Mem Commit"
        )
        self.add_chart(self.memory_commit_chart)

        self.disk0_chart = TimeSeries(root, outline="forestgreen", title="Disk0 Active")
        self.add_chart(self.disk0_chart)
        self.disk1_chart = TimeSeries(root, outline="forestgreen", title="Disk1 Active")
        self.add_chart(self.disk1_chart)
        if len(self.chart_list) % 2 == 1:
            self.add_chart(EmptyChart())
        self.network_chart_received = TimeSeries(
            root,
            outline="saddlebrown",
            title="Net Rx",
            unit=" Mbps",
            decimal_places=2,
            max_value=1000,
            log_scale=True,
        )
        self.add_chart(self.network_chart_received)
        self.network_chart_sent = TimeSeries(
            root,
            outline="saddlebrown",
            title="Net Tx",
            unit=" Mbps",
            decimal_places=2,
            max_value=1000,
            log_scale=True,
        )
        self.add_chart(self.network_chart_sent)
        self.logical_disk_usage_chart = DiskProgressBars(root, title="Disk Usage")
        self.add_chart(self.logical_disk_usage_chart)

        self.gpu_chart = TimeSeries(
            root, outline="steelblue", title="GPU Usage", unit=" %", decimal_places=1
        )
        self.add_chart(self.gpu_chart)

        self.engine = MetricEngine(interval=1, history_size=600)
        self.engine.register_collector(RemoteMetricsCollector(exporter_url))
        self.engine.register_analyzer(CpuUsageAnalyzer())
        self.engine.register_analyzer(MemoryUsageAnalyzer())
        self.engine.register_analyzer(PhysicalDiskActiveTimeAnalyzer())
        self.engine.register_analyzer(NetworkSpeedAnalyzerV2())
        self.engine.register_analyzer(MemoryCommitAnalyzer())
        self.engine.register_analyzer(LogicalDiskSizeAnalyzer())
        self.engine.register_analyzer(GpuUsageAnalyzer())

        # 用于保存历史数据，便于后续画图
        self.scrape_time = 0
        self.cpu_history: list[tuple[float, float]] = []
        self.memory_history: list[tuple[float, float]] = []
        self.disk0_history: list[tuple[float, float]] = []
        self.disk1_history: list[tuple[float, float]] = []
        self.network_history_received: list[tuple[float, float]] = []
        self.network_history_sent: list[tuple[float, float]] = []
        self.cpu_heatmap_history: list[tuple[float, list[float]]] = []
        self.memory_commit_history: list[tuple[float, float]] = []
        self.logical_disk_space_values: list[tuple[str, float, float]] = []
        self.gpu_history: list[tuple[float, float]] = []

        self.root.after_idle(self.check_queue)

        # 启动引擎
        self.engine.register_on_update(self.refresh_ui)
        self.engine.start()

    def add_chart(self, chart: Chart):
        """
        添加图表到指定的行和列
        :param chart: 要添加的图表
        """
        row = len(self.chart_list) % 2
        column = len(self.chart_list) // 2
        chart.grid(row=row, column=column, padx=2, pady=2, sticky="nsew")
        self.chart_list.append(chart)
        # 设置行和列的权重，使其可以自适应窗口大小
        self.root.grid_rowconfigure(row, weight=1)
        self.root.grid_columnconfigure(column, weight=1)

    def update_metrics(self):
        scrape_time = self.engine.get_last_scrape_time()
        cpu_usage_metrics = self.engine.get_metric_range(
            "cpu_usage_percent", scrape_time - 61, scrape_time
        )
        memory_usage_metrics = self.engine.get_metric_range(
            "memory_usage_percent", scrape_time - 61, scrape_time
        )
        memory_commit_metrics = self.engine.get_metric_range(
            "memory_commit_rate_percent", scrape_time - 61, scrape_time
        )
        disk_usage_metrics = self.engine.get_metric_range(
            "disk_io_util_percent", scrape_time - 61, scrape_time
        )
        network_usage_metrics = self.engine.get_metric_range(
            "network_speed_mbps", scrape_time - 61, scrape_time
        )
        logical_disk_total_metrics = self.engine.get_metric("logical_disk_size_bytes")
        logical_disk_free_metrics = self.engine.get_metric("logical_disk_free_bytes")
        gpu_usage_metrics = self.engine.get_metric_range(
            "gpu_usage_percent", scrape_time - 61, scrape_time
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
        self.memory_commit_history = get_value_from_metric(memory_commit_metrics)
        self.memory_commit_chart.update_values(
            self.memory_commit_history, self.scrape_time - 60, self.scrape_time
        )
        self.disk0_history = get_value_from_metric(disk_usage_metrics, {"disk": "0"})
        self.disk1_history = get_value_from_metric(disk_usage_metrics, {"disk": "1"})
        self.disk0_chart.update_values(
            self.disk0_history, self.scrape_time - 60, self.scrape_time
        )
        self.disk1_chart.update_values(
            self.disk1_history, self.scrape_time - 60, self.scrape_time
        )
        self.network_history_received = get_value_from_metric(
            network_usage_metrics, {"direction": "received"}
        )
        self.network_chart_received.update_values(
            self.network_history_received, self.scrape_time - 60, self.scrape_time
        )
        self.network_history_sent = get_value_from_metric(
            network_usage_metrics, {"direction": "sent"}
        )
        self.network_chart_sent.update_values(
            self.network_history_sent, self.scrape_time - 60, self.scrape_time
        )

        logical_disk_space_values_map: dict[str, tuple[float, float]] = {}
        if logical_disk_total_metrics:
            for disk in logical_disk_total_metrics.samples:
                disk_name = disk.labels.get("volume", "")
                if not disk_name:
                    continue
                logical_disk_space_values_map[disk_name] = (0, disk.value)
            for disk in logical_disk_free_metrics.samples:
                disk_name = disk.labels.get("volume", "")
                if disk_name not in logical_disk_space_values_map:
                    continue
                logical_disk_space_values_map[disk_name] = (
                    disk.value,
                    logical_disk_space_values_map[disk_name][1],
                )
            self.logical_disk_space_values = [
                (disk_name, free_space, total_space)
                for disk_name, (
                    free_space,
                    total_space,
                ) in logical_disk_space_values_map.items()
            ]
            self.logical_disk_usage_chart.update_values(self.logical_disk_space_values)

        heatmap_map = get_value_from_metric_group_by(
            cpu_usage_metrics,
            ["core"],
        )

        # 处理 CPU 热力图数据
        def sort_key(item):
            x, y = map(int, item[0].split(","))
            return (x + 1) * y

        self.cpu_heatmap_history = [
            (timestamp, [value for _, value in sorted(values.items(), key=sort_key)])
            for timestamp, values in heatmap_map
        ]
        self.cpu_heatmap_chart.update_values(
            self.cpu_heatmap_history, self.scrape_time - 60, self.scrape_time
        )
        self.gpu_history = get_value_from_metric(gpu_usage_metrics, {"device": "0"})
        self.gpu_chart.update_values(
            self.gpu_history, self.scrape_time - 60, self.scrape_time
        )

    def draw_charts(self):
        for chart in self.chart_list:
            chart.draw_chart()

    def refresh_ui(self):
        self.update_metrics()
        self.q.put("refresh")
        # self.root.after_idle(self.draw_charts)

    def check_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                if msg == "refresh":
                    self.root.after_idle(self.draw_charts)
        except queue.Empty:
            pass
        self.root.after(50, self.check_queue)

    def add_right_click_exit_menu(self):
        # 创建只含有“退出”选项的菜单
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="退出", command=self.root.quit)

        # 右键弹出菜单的回调
        def show_menu(event):
            menu.post(event.x_root, event.y_root)

        # 绑定右键事件（Windows/Linux）
        self.root.bind("<Button-3>", show_menu)

    def mainloop(self):
        self.root.mainloop()
        self.engine.stop()
