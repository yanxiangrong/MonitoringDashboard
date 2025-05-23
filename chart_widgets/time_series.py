import math

from chart_widgets.chart import Chart
from chart_widgets.utils import rgb_to_hex, blend_color


class TimeSeries(Chart):
    def __init__(self, master=None, **kwargs):
        self.outline = kwargs.pop("outline", "steelblue")
        self.title = kwargs.pop("title", "")
        self.decimal_places = kwargs.pop("decimal_places", 1)
        self.unit = kwargs.pop("unit", "%")
        self.max_value = kwargs.pop("max_value", 100)
        self.min_value = kwargs.pop("min_value", 0)
        self.log_scale = kwargs.pop("log_scale", False)

        super().__init__(master, **kwargs)

        self.values: list[tuple[float, float]] = []
        self.start_time = 0
        self.end_time = 0
        self.fill = rgb_to_hex(
            blend_color(self.winfo_rgb(self.outline), self.winfo_rgb(self["bg"]), 0.25)
        )

    def update_values(
        self,
        values: list[tuple[float, float]],
        start_time: float,
        end_time: float,
    ):
        self.values = values
        self.start_time = start_time
        self.end_time = end_time

    def draw_chart(self):
        content_x, content_y, content_w, content_h = self.content_rect

        if content_w <= 1 or content_h <= 1:
            return

        self.draw_clear()

        # 画内部网格
        dt = self.end_time - self.start_time
        offset = self.end_time % (dt / 10) if dt > 0 else 0
        for i in range(0, 10):
            x = (
                int(((i + 1) / 10 - (offset / dt if dt > 0 else 0)) * content_w)
                + content_x
            )
            self.create_line(
                x,
                content_y,
                x,
                content_y + content_h - 1,
                fill="lightgray",
                dash=(2, 2),
            )
            if i > 0:
                y = int(i * content_h / 10) + content_y
                self.create_line(
                    content_x,
                    y,
                    content_x + content_w - 1,
                    y,
                    fill="lightgray",
                    dash=(2, 2),
                )

        # 画填充折线（面积图）
        if self.values and self.values[-1][0] > self.start_time:
            # 计算所有点
            points = []
            for ts, val in self.values:
                x = int((ts - self.start_time) * content_w / dt) + content_x
                if self.log_scale:
                    c = 0.1
                    norm = (math.log10(val + c) - math.log10(self.min_value + c)) / (
                        math.log10(self.max_value + c) - math.log10(self.min_value + c)
                    )
                else:
                    norm = (
                        (val - self.min_value) / (self.max_value - self.min_value)
                        if self.max_value > self.min_value
                        else 0
                    )
                y = int(content_h - norm * content_h + content_y)

                points.append((x, y))
            # 构造多边形点序列（首尾加底边）
            if len(points) >= 2:
                poly_points = (
                    [(points[0][0], content_y + content_h - 1)]
                    + points
                    + [(points[-1][0], content_y + content_h - 1)]
                )
                # 转为一维坐标序列
                poly_coords = [coord for point in poly_points for coord in point]
                self.create_polygon(
                    poly_coords, fill=self.fill, outline=self.outline, width=1
                )
        else:
            self.draw_no_data()

        # 画边框
        self.draw_border()

        # 画标题
        if self.title:
            self.create_text(
                content_x + 5,
                content_y + 5,
                text=self.title,
                anchor="nw",
            )
        # 画数值
        if self.values and self.values[-1][0] == self.end_time:
            value_text = f"{self.values[-1][1]:.{self.decimal_places}f}{self.unit}"
        else:
            value_text = "No Data"
        self.create_text(
            content_x + content_w - 5,
            content_y + 5,
            text=value_text,
            anchor="ne",
        )
