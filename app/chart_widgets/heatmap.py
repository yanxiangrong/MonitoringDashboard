from .chart import Chart


class Heatmap(Chart):
    """
    A class to represent a heatmap chart.
    """

    def __init__(self, master=None, **kwargs):
        """
        Initialize the heatmap chart.

        Args:
            master: The parent widget.
            **kwargs: Additional keyword arguments.
        """

        self.max_value = float(kwargs.pop("max_value", 100))
        self.min_value = float(kwargs.pop("min_value", 0))
        self.title = kwargs.pop("title", "")

        super().__init__(master, **kwargs)

        self.values: list[tuple[float, list[float]]] = []
        self.start_time = 0
        self.end_time = 0

    def update_values(
        self,
        values: list[tuple[float, list[float]]],
        start_time: float,
        end_time: float,
    ):
        """
        Update the values for the heatmap.

        Args:
            values: The new values for the heatmap.
            start_time: The start time for the heatmap.
            end_time: The end time for the heatmap.
        """

        self.values = values
        self.start_time = start_time
        self.end_time = end_time

    def draw_chart(self):
        """
        Draw the heatmap chart.
        This method should be overridden in subclasses to provide the actual drawing logic.
        """
        content_x, content_y, content_w, content_h = self.content_rect

        if content_w <= 1 or content_h <= 1:
            return

        self.draw_clear()

        # Draw the heatmap
        if self.values and self.values[-1][0] > self.start_time:
            for value in self.values:
                timestamp, data = value
                x = (
                    int(
                        (timestamp - self.start_time)
                        / (self.end_time - self.start_time)
                        * content_w
                    )
                    + content_x
                )
                for i, val in enumerate(data):
                    val = max(self.min_value, min(val, self.max_value))
                    h = int((content_h - 2) / len(data)) + 1
                    w = int(content_w / 20)
                    y = int(i * (content_h - 2) / len(data) + content_y + 1)
                    color = self.get_color(val)
                    self.create_rectangle(x, y, x + w, y + h, fill=color, outline="")
            # 画内部网格
            series_count = len(self.values[-1][1])
            for i in range(1, series_count):
                y = int(i * (content_h - 2) / series_count + content_y + 1)
                self.create_line(
                    content_x,
                    y,
                    content_x + content_w - 1,
                    y,
                    fill="lightgray",
                    dash=(2, 2),
                )
        else:
            self.draw_no_data()
        self.draw_border()

        # 画标题
        if self.title:
            self.create_text(
                content_x + 5,
                content_y + 5,
                text=self.title,
                anchor="nw",
            )

    def get_color(self, value: float) -> str:
        """
        Get the color for a given value.

        Args:
            value: The value to get the color for.

        Returns:
            The color as a hex string.
        """

        brightness = 0.6
        saturation = 0.75

        # 1. 归一化RGB
        normalized_value = min(
            max((value - self.min_value) / (self.max_value - self.min_value), 0), 1
        )
        if normalized_value < 0.5:
            r = normalized_value * 2
            g = 1.0
        else:
            r = 1.0
            g = 1.0 - (normalized_value - 0.5) * 2
        b = 0.0

        # 2. 计算当前亮度
        current_luminance = 0.299 * r + 0.587 * g + 0.114 * b

        # 3. 目标亮度
        target_luminance = brightness

        # 4. 计算缩放因子
        if current_luminance == 0:
            scale = 0
        else:
            scale = target_luminance / current_luminance

        # 5. 缩放到目标亮度
        r = min(max(r * scale, 0), 1)
        g = min(max(g * scale, 0), 1)
        b = min(max(b * scale, 0), 1)

        # 6. 转为 0~255
        r255 = r * 255
        g255 = g * 255
        b255 = b * 255

        # 7. 降低饱和度到0.8
        gray = 0.299 * r255 + 0.587 * g255 + 0.114 * b255
        r255 = r255 * saturation + gray * (1 - saturation)
        g255 = g255 * saturation + gray * (1 - saturation)
        b255 = b255 * saturation + gray * (1 - saturation)

        # 8. 四舍五入并转为整数
        r_final = round(r255)
        g_final = round(g255)
        b_final = round(b255)
        return f"#{r_final:02x}{g_final:02x}{b_final:02x}"
