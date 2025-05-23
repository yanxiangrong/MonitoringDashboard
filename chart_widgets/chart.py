import tkinter as tk
from abc import abstractmethod


class Chart(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        kwargs |= {
            "highlightthickness": 0,
        }

        super().__init__(master, **kwargs)

        self.content_rect = (0, 0, 0, 0)
        self.bind("<Configure>", self.on_configure)

    def on_configure(self, _event):
        border = int(self["borderwidth"])
        highlight = int(self["highlightthickness"])
        self.content_rect = (
            border + highlight,
            border + highlight,
            self.winfo_width() - 2 * (border + highlight),
            self.winfo_height() - 2 * (border + highlight),
        )
        self.after_idle(self.draw_chart)

    @abstractmethod
    def draw_chart(self):
        """
        绘制图表
        """
        raise NotImplementedError("Subclasses must implement draw_chart method")

    def draw_no_data(self):
        content_x, content_y, content_w, content_h = self.content_rect
        text = "No Data"
        font_size_h = int(content_h * 0.2)
        max_char_width = 0.6
        font_size_w = int(content_w * 0.8 / (len(text) * max_char_width))
        font_size = max(12, min(font_size_h, font_size_w))
        self.create_text(
            content_x + content_w // 2,
            content_y + content_h // 2,
            text=text,
            fill="gray",
            font=("Arial", font_size, "bold"),
        )

    def draw_border(self):
        content_x, content_y, content_w, content_h = self.content_rect
        # 画边框
        self.create_rectangle(
            content_x,
            content_y,
            content_x + content_w - 1,
            content_y + content_h - 1,
            outline="dimgray",
            width=1,
        )

    def draw_clear(self):
        self.delete("all")


class EmptyChart(Chart):
    def draw_chart(self):
        pass
