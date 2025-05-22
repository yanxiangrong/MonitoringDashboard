import tkinter as tk

from chart_widgets.time_series import TimeSeries
from metrics.analyze import CpuUsageAnalyzer, MemoryTrendAnalyzer
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine
from metrics.index import get_value_from_metric

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("MonitoringDashboard")
        self.w, self.h = 600, 400
        self.root.geometry(f"{self.w}x{self.h}")
        self.cpu_chart = TimeSeries(root, outline="steelblue", title="CPU Usage")
        self.cpu_chart.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        self.memory_chart = TimeSeries(root, outline="slateblue", title="Memory Usage")
        self.memory_chart.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        # 设置行和列的权重
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        # root.grid_columnconfigure(1, weight=1)

        # limegreen saddlebrown
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

        # 绘制 CPU 使用率图表
        self.cpu_chart.update_values(
            self.cpu_history, self.scrape_time - 60, self.scrape_time
        )
        self.cpu_chart.update_value_text(f"{self.cpu_history[-1][1]:.1f}%")

        # 绘制内存使用率图表
        self.memory_chart.update_values(
            self.memory_history, self.scrape_time - 60, self.scrape_time
        )
        self.memory_chart.update_value_text(f"{self.memory_history[-1][1]:.1f}%")

    def draw_charts(self):
        # 更新 UI 的逻辑
        self.cpu_chart.draw_chart()
        self.memory_chart.draw_chart()

    def refresh_ui(self):
        # 每秒刷新一次
        self.update_metrics()
        self.root.after_idle(self.draw_charts)

    def mainloop(self):
        self.root.mainloop()
        self.engine.stop()


def main():
    root = tk.Tk()
    app = MonitoringDashboardApp(root)
    app.mainloop()


if __name__ == "__main__":
    main()
