import tkinter as tk

from .chart_widgets.chart import EmptyChart, Chart
from .chart_widgets.heatmap import Heatmap
from .chart_widgets.progress_bar import DiskProgressBars
from .chart_widgets.time_series import TimeSeries


class ChartManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.charts = []
        self._init_charts()

    def _init_charts(self):
        self.cpu_chart = TimeSeries(self.root, outline="steelblue", title="CPU Usage")
        self.add_chart(self.cpu_chart)
        self.cpu_heatmap_chart = Heatmap(self.root, title="CPUs Usage")
        self.add_chart(self.cpu_heatmap_chart)

        self.memory_chart = TimeSeries(
            self.root, outline="slateblue", title="Mem Usage"
        )
        self.add_chart(self.memory_chart)
        self.memory_commit_chart = TimeSeries(
            self.root, outline="slateblue", title="Mem Commit"
        )
        self.add_chart(self.memory_commit_chart)

        self.disk0_chart = TimeSeries(
            self.root, outline="forestgreen", title="Disk0 Active"
        )
        self.add_chart(self.disk0_chart)
        self.disk1_chart = TimeSeries(
            self.root, outline="forestgreen", title="Disk1 Active"
        )
        self.add_chart(self.disk1_chart)
        if len(self.charts) % 2 == 1:
            self.add_chart(EmptyChart())
        self.network_chart_received = TimeSeries(
            self.root,
            outline="saddlebrown",
            title="Net Rx",
            unit=" Mbps",
            decimal_places=2,
            max_value=1000,
            log_scale=True,
        )
        self.add_chart(self.network_chart_received)
        self.network_chart_sent = TimeSeries(
            self.root,
            outline="saddlebrown",
            title="Net Tx",
            unit=" Mbps",
            decimal_places=2,
            max_value=1000,
            log_scale=True,
        )
        self.add_chart(self.network_chart_sent)
        self.logical_disk_usage_chart = DiskProgressBars(self.root, title="Disk Usage")
        self.add_chart(self.logical_disk_usage_chart)

        self.gpu_chart = TimeSeries(
            self.root,
            outline="steelblue",
            title="GPU Usage",
            unit=" %",
            decimal_places=1,
        )
        self.add_chart(self.gpu_chart)

    def add_chart(self, chart: Chart):
        """
        添加图表到指定的行和列
        :param chart: 要添加的图表
        """
        # 负责布局和管理

        row = len(self.charts) % 2
        column = len(self.charts) // 2
        chart.grid(row=row, column=column, padx=2, pady=2, sticky="nsew")
        self.charts.append(chart)
        # 设置行和列的权重，使其可以自适应窗口大小
        self.root.grid_rowconfigure(row, weight=1)
        self.root.grid_columnconfigure(column, weight=1)

    def draw_charts(self):
        for chart in self.charts:
            chart.draw_chart()
