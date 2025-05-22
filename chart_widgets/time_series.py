import tkinter as tk

from chart_widgets.utils import rgb_to_hex, blend_color


class TimeSeries(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        self.outline = kwargs.pop("outline", "steelblue")
        self.title = kwargs.pop("title", "")
        self.value_text = kwargs.pop("value_text", "")
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

        self.bind("<Configure>", self.on_configure)

    def on_configure(self, _event):
        self.after_idle(self.draw_chart)

    def update_values(
        self,
        values: list[tuple[float, float]],
        start_time: float,
        end_time: float,
    ):
        self.values = values
        self.start_time = start_time
        self.end_time = end_time

    def update_value_text(self, value_text: str):
        self.value_text = value_text

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
        offset = self.end_time % (dt / 10) if dt > 0 else 0
        for i in range(0, 10):
            x = int(((i + 1) / 10 - (offset / dt if dt > 0 else 0)) * w) + x0
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
                norm = (
                    (val - self.min_value) / (self.max_value - self.min_value)
                    if self.max_value > self.min_value
                    else 0
                )
                y = int(h - norm * h + y0)

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

        # 画标题
        if self.title:
            self.create_text(
                x0 + 5,
                y0 + 5,
                text=self.title,
                anchor="nw",
            )
        # 画数值
        if self.value_text:
            self.create_text(
                x0 + w - 5,
                y0 + 5,
                text=self.value_text,
                anchor="ne",
            )
