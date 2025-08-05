import tkinter as tk
from tkinter import ttk

from .chart import Chart


class ProgressBar(Chart):
    """
    A class to represent a progress bar chart.
    """

    def __init__(self, master=None, **kwargs):
        """
        Initialize the progress bar chart.

        Args:
            master: The parent widget.
            **kwargs: Additional keyword arguments.
        """
        self.max_value = float(kwargs.pop("max_value", 100))
        self.min_value = float(kwargs.pop("min_value", 0))
        self.value = float(kwargs.pop("value", 0))
        self.level_color = kwargs.pop(
            "level_color",
            [(90, "#26a0da"), (100, "#da2626")],
        )

        super().__init__(master, **kwargs)

    def update_values(
        self,
        value: float,
    ):
        """
        Update the progress bar with a new value.

        Args:
            value: The new value to update the progress bar.
        """
        self.value = value

    def draw_chart(self):
        """
        Draw the progress bar chart.
        """
        content_x, content_y, content_w, content_h = self.content_rect

        if content_w <= 1 or content_h <= 1:
            return

        self.draw_clear()

        # Draw the progress barfloat()
        self.value = max(self.min_value, min(self.value, self.max_value))
        progress = (self.value - self.min_value) / (self.max_value - self.min_value)
        progress = max(0.0, min(progress, 1.0))
        fill_width = round((content_w - 2) * progress)

        # Draw the filled part of the progress bar
        fill_color = ""
        for level in self.level_color:
            if self.value <= level[0]:
                fill_color = level[1]
                break
        self.create_rectangle(
            content_x + 1,
            content_y + 1,
            content_x + fill_width + 1,
            content_y + content_h - 1,
            fill=fill_color,
            outline="",
        )
        # Draw the non-filled part of the progress bar
        self.create_rectangle(
            content_x + fill_width + 1,
            content_y + 1,
            content_x + content_w - 2,
            content_y + content_h - 1,
            fill="#e6e6e6",
            outline="",
        )
        # Draw the border
        self.create_rectangle(
            content_x,
            content_y,
            content_x + content_w - 1,
            content_y + content_h - 1,
            outline="#bcbcbc",
            width=1,
        )


class DiskProgressBars(Chart):
    """
    A class to represent a set of disk progress bars.
    """

    def __init__(self, master=None, **kwargs):
        """
        Initialize the disk progress bars.

        Args:
            master: The parent widget.
            **kwargs: Additional keyword arguments.
        """

        self.title = kwargs.pop("title", "")
        super().__init__(master, **kwargs)
        self.disk_labels: list[ttk.Label] = []
        self.disk_size_labels: list[ttk.Label] = []
        self.disk_bars: list[ProgressBar] = []
        self.frame = tk.Frame(self)
        self.disk_data: list[tuple[str, float, float]] = []

        ttk.Label(
            self.frame,
            text=self.title,
        ).grid(row=0, column=0, sticky=tk.NW, columnspan=2, padx=(2, 0), pady=(2, 0))
        self.frame.columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure("My.TLabel", padding=0)

    def on_configure(self, _event):
        """
        Handle the configuration event.

        Args:
            _event: The event object.
        """
        super().on_configure(_event)
        self.frame.place(
            x=self.content_rect[0] + 1,
            y=self.content_rect[1] + 1,
            width=self.content_rect[2] - 2,
            height=self.content_rect[3] - 2,
        )

    def update_values(
        self,
        disk_data: list[tuple[str, float, float]],
    ):
        """
        Update the disk progress bars with new values.

        Args:
            disk_data: A list of tuples containing disk name, used space, and total space.
        """
        self.disk_data = disk_data

    def draw_chart(self):
        content_x, content_y, content_w, content_h = self.content_rect

        if content_w <= 1 or content_h <= 1:
            return

        self.draw_clear()

        if self.disk_data:
            self.frame.place(
                x=self.content_rect[0] + 1,
                y=self.content_rect[1] + 1,
                width=self.content_rect[2] - 2,
                height=self.content_rect[3] - 2,
            )

            row = 1
            for idx, (disk_name, free_space, total_space) in enumerate(self.disk_data):
                percent = (total_space - free_space) / total_space * 100
                value = round(percent)
                if self.winfo_width() >= 170:
                    disk_size = convert_bytes(total_space)
                    free_size = convert_bytes(free_space)
                    text = f"{free_size} / {disk_size} ({percent:.3g}%)"
                elif self.winfo_width() >= 150:
                    disk_size = convert_bytes2(free_space, total_space)
                    text = f"{disk_size} ({percent:.3g}%)"
                else:
                    free_size = convert_bytes(free_space)
                    text = f"{free_size} ({percent:.3g}%)"

                if idx >= len(self.disk_bars):
                    disk_size_label = ttk.Label(self.frame, text=text)
                    disk_size_label.grid(
                        row=row,
                        column=0,
                        columnspan=2,
                        sticky=tk.E,
                        padx=5,
                        pady=(5, 0),
                    )
                    self.disk_size_labels.append(disk_size_label)
                    row += 1

                    label = ttk.Label(self.frame, text=disk_name)
                    label.grid(row=row, column=0, sticky=tk.E, padx=(5, 2))
                    self.disk_labels.append(label)
                    progress_bar = ProgressBar(
                        master=self.frame, value=value, height=15
                    )
                    progress_bar.grid(row=row, column=1, sticky=tk.EW, padx=(2, 5))
                    self.disk_bars.append(progress_bar)
                    row += 1
                else:
                    self.disk_size_labels[idx].config(text=text)
                    self.disk_labels[idx].config(text=disk_name)
                    self.disk_bars[idx].update_values(value)

                self.disk_bars[idx].draw_chart()

            if len(self.disk_bars) > len(self.disk_data):
                for i in range(len(self.disk_data), len(self.disk_bars)):
                    self.disk_bars[i].grid_forget()
                    self.disk_bars[i].destroy()
                self.disk_bars = self.disk_bars[: len(self.disk_data)]
        else:
            self.frame.place_forget()
            self.draw_no_data()
        self.draw_border()
        # Draw the title
        if self.title:
            self.create_text(
                content_x + 5,
                content_y + 5,
                text=self.title,
                anchor="nw",
            )


# 字节转 KB/MB/GB/TB/PB/EB
def convert_bytes(num: float) -> str:
    """
    Convert bytes to a human-readable format.

    Args:
        num: The number of bytes.

    Returns:
        A string representing the size in a human-readable format.
    """
    for x in ["bytes", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if num < 1024.0:
            break
        num /= 1024.0
    return f"{num:.3g} {x}"


def convert_bytes2(num1: float, num2: float) -> str:
    """
    Convert bytes to a human-readable format for two values.

    Args:
        num1: The first number of bytes.
        num2: The second number of bytes.

    Returns:
        A string representing the size in a human-readable format.
    """

    for x in ["bytes", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if num1 < 1024.0 and num2 < 1024.0:
            break
        num1 /= 1024.0
        num2 /= 1024.0
    return f"{num1:.3g} / {num2:.3g} {x}"
