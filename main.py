import time
import tkinter as tk
from typing import Iterable

from metrics.analyze import CpuUsageAnalyzer, MemoryTrendAnalyzer
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine
from metrics.index import get_value_from_metric

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


class LineChart(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.values: Iterable[float] | None = None
        self.max_value = 100
        self.min_value = 0

    def update_values(self, values: Iterable[float]):
        self.values = values
        self.draw_chart()

    def draw_chart(self):
        self.delete("all")
        # 画图逻辑
        w, h = self.winfo_width(), self.winfo_height()
        x_step = 5

        points_last: tuple[int, int] | None = None
        for i, val in enumerate(self.values):
            x = w - i * x_step
            y = int(h - (val - self.min_value) * h / (self.max_value - self.min_value))
            if points_last is not None:
                x0, y0 = points_last
                self.create_line(x0, y, x, y, fill="blue", width=1)
            points_last = (x, y)


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("MonitoringDashboard")
        self.w, self.h = 600, 400
        self.chart = LineChart(root, width=600, height=300)
        self.chart.pack()

        self.engine = MetricEngine(interval=1, history_size=600)
        self.engine.register_collector(RemoteMetricsCollector(EXPORTER_URL))
        self.engine.register_analyzer(CpuUsageAnalyzer())
        self.engine.register_analyzer(MemoryTrendAnalyzer())

        # 用于保存历史数据，便于后续画图
        self.cpu_history = []
        self.memory_history = []

        # 启动引擎
        self.engine.register_on_update(self.refresh_ui)
        self.engine.start()

    def update_metrics(self):
        now = time.time()
        cpu_usage_metrics = self.engine.get_metric_range(
            "cpu_usage_percent", now - 60, now
        )
        memory_usage_metrics = self.engine.get_metric_range(
            "memory_usage_percent", now - 60, now
        )

        self.cpu_history = get_value_from_metric(cpu_usage_metrics)
        self.memory_history = get_value_from_metric(memory_usage_metrics)

    def refresh_ui(self):
        # 每秒刷新一次
        self.update_metrics()
        self.root.after(0, self.draw_metrics)

    def draw_metrics(self):
        # 绘制 CPU 使用率图表
        self.chart.update_values(self.cpu_history)
        # self.chart.create_text(10, 10, text="CPU Usage", anchor="nw")

        # 绘制内存使用率图表
        # self.chart.update_values(self.memory_history)
        # self.chart.create_text(10, 30, text="Memory Usage", anchor="nw")

    def mainloop(self):
        self.root.mainloop()
        self.engine.stop()


def main():
    root = tk.Tk()
    app = MonitoringDashboardApp(root)
    app.mainloop()


if __name__ == "__main__":
    main()
