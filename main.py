import tkinter as tk

from metrics.analyze import CpuUsageAnalyzer, MemoryTrendAnalyzer
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine
from metrics.index import get_value_from_metric

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


class TimeSeries(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        kwargs |= {
            "highlightthickness": 0,
        }
        super().__init__(master, **kwargs)
        self.values: list[tuple[float, float]] = []
        self.max_value = 100
        self.min_value = 0
        self.start_time = 0
        self.end_time = 0

    def update_values(
        self,
        values: list[tuple[float, float]],
        start_time: float,
        end_time: float,
    ):
        self.values = values
        self.start_time = start_time
        self.end_time = end_time
        self.draw_chart()

    def draw_chart(self):
        self.delete("all")
        # 画图逻辑
        border = int(self["borderwidth"])
        highlight = int(self["highlightthickness"])
        x0 = border + highlight
        y0 = border + highlight
        w, h = self.winfo_width() - x0, self.winfo_height() - y0
        if w <= 1 or h <= 1:
            return

        # 画内部网格
        dt = self.end_time - self.start_time
        for i in range(1, 10):
            offset = self.end_time % (dt / 10)
            x = int(((i + 1) / 10 - offset / dt) * w)
            self.create_line(x, y0, x, h - 1, fill="lightgray", dash=(2, 2))
            y = int(i * h / 10)
            self.create_line(x0, y, w - 1, y, fill="lightgray", dash=(2, 2))

        # 画折线
        points_last: tuple[int, int] | None = None
        for ts, val in self.values:
            x = int((ts - self.start_time) * w / dt)
            y = int(h - (val - self.min_value) * h / dt)
            if points_last is not None:
                x1, y1 = points_last
                self.create_line(x1, y1, x, y, fill="blue", width=1)
            points_last = (x, y)

        # 画边框
        self.create_rectangle(x0, y0, w - 1, h - 1, outline="black", width=1)


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("MonitoringDashboard")
        self.w, self.h = 600, 400
        self.chart = TimeSeries(root, width=600, height=300)
        self.chart.pack()

        self.engine = MetricEngine(interval=1, history_size=600)
        self.engine.register_collector(RemoteMetricsCollector(EXPORTER_URL))
        self.engine.register_analyzer(CpuUsageAnalyzer())
        self.engine.register_analyzer(MemoryTrendAnalyzer())

        # 用于保存历史数据，便于后续画图
        self.cpu_history: list[tuple[float, float]] = []
        self.memory_history: list[tuple[float, float]] = []
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

        self.scrape_time = scrape_time
        self.cpu_history = get_value_from_metric(cpu_usage_metrics)
        self.memory_history = get_value_from_metric(memory_usage_metrics)

    def refresh_ui(self):
        # 每秒刷新一次
        self.update_metrics()
        self.root.after(0, self.draw_metrics)

    def draw_metrics(self):
        # 绘制 CPU 使用率图表
        self.chart.update_values(
            self.cpu_history, self.scrape_time - 60, self.scrape_time
        )
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
