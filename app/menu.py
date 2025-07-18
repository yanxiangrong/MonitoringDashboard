import tkinter as tk


def add_right_click_exit_menu(root: tk.Tk):
    # 创建只含有“退出”选项的菜单
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="退出", command=root.quit)

    # 右键弹出菜单的回调
    def show_menu(event):
        menu.post(event.x_root, event.y_root)

    # 绑定右键事件（Windows/Linux）
    root.bind("<Button-3>", show_menu)
