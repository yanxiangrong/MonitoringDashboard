import tkinter as tk

from metrics.analyze import CpuUsageAnalyzer, MemoryTrendAnalyzer
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine
from metrics.index import get_value_from_metric

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


class TimeSeries(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        self.outline = kwargs.pop("outline", "steelblue")
        kwargs |= {
            "highlightthickness": 0,
        }
        super().__init__(master, **kwargs)
        self.values: list[tuple[float, float]] = []
        self.max_value = 100
        self.min_value = 0
        self.start_time = 0
        self.end_time = 0
        self.fill = rgb_to_hex(
            blend_color(self.winfo_rgb(self.outline), self.winfo_rgb(self["bg"]), 0.25)
        )

        self.bind("<Configure>", lambda _e: self.draw_chart())

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
        w, h = self.winfo_width() - 2 * x0, self.winfo_height() - 2 * y0
        if w <= 1 or h <= 1:
            return

        # 画内部网格
        dt = self.end_time - self.start_time
        offset = self.end_time % (dt / 10)
        for i in range(0, 10):
            x = int(((i + 1) / 10 - offset / dt) * w) + x0
            self.create_line(x, y0, x, y0 + h - 1, fill="lightgray", dash=(2, 2))
            if i > 0:
                y = int(i * h / 10) + y0
                self.create_line(x0, y, x0 + w - 1, y, fill="lightgray", dash=(2, 2))

        # 画填充折线（面积图）
        if self.values:
            # 计算所有点
            points = []
            for ts, val in self.values:
                x = int((ts - self.start_time) * w / dt) + x0
                y = (
                    int(
                        h
                        - (val - self.min_value) * h / (self.max_value - self.min_value)
                    )
                    + y0
                )
                points.append((x, y))
            # 构造多边形点序列（首尾加底边）
            if len(points) >= 2:
                poly_points = (
                    [(points[0][0], y0 + h - 1)]
                    + points
                    + [(points[-1][0], y0 + h - 1)]
                )
                # 转为一维坐标序列
                poly_coords = [coord for point in poly_points for coord in point]
                self.create_polygon(
                    poly_coords, fill=self.fill, outline=self.outline, width=1
                )

        # 画边框
        self.create_rectangle(
            x0, y0, x0 + w - 1, y0 + h - 1, outline="dimgray", width=1
        )


class MonitoringDashboardApp:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("MonitoringDashboard")
        self.w, self.h = 600, 400
        self.root.geometry(f"{self.w}x{self.h}")
        self.cpu_chart = TimeSeries(root, outline="steelblue")
        self.cpu_chart.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        self.memory_chart = TimeSeries(root, outline="slateblue")
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

    def refresh_ui(self):
        # 每秒刷新一次
        self.update_metrics()
        self.root.after(0, self.draw_metrics)

    def draw_metrics(self):
        # 绘制 CPU 使用率图表
        self.cpu_chart.update_values(
            self.cpu_history, self.scrape_time - 60, self.scrape_time
        )
        self.cpu_chart.create_text(10, 10, text="CPU Usage", anchor="nw")

        # 绘制内存使用率图表
        self.memory_chart.update_values(
            self.memory_history, self.scrape_time - 60, self.scrape_time
        )
        self.memory_chart.create_text(10, 10, text="Memory Usage", anchor="nw")

    def mainloop(self):
        self.root.mainloop()
        self.engine.stop()


def blend_color(fg, bg, alpha):
    """fg, bg: (r, g, b), alpha: 0~1"""
    return tuple(int(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def main():
    root = tk.Tk()
    app = MonitoringDashboardApp(root)
    app.mainloop()


if __name__ == "__main__":
    main()
