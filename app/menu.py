import tkinter as tk


def add_right_click_exit_menu(root):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="退出", command=root.quit)

    def show_menu(event):
        menu.post(event.x_root, event.y_root)

    root.bind("<Button-3>", show_menu)
