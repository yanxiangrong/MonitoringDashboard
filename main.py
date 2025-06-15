import argparse
import ctypes

import pygame

from config import DEFAULT_EXPORTER_URL

# 普通字体列表
normal_fonts = [
    "PibotoLt", "DejaVu Sans", "Segoe UI", "Microsoft YaHei UI", "Arial"
]

# 等宽字体列表
monospace_fonts = [
    "Consolas", "DejaVu Sans Mono", "monospace"
]

# 中文字体列表
chinese_fonts = [
    "WenQuanYi Zen Hei", "Microsoft YaHei", "SimSun"
]


def get_font(font_list, size):
    """返回第一个可用字体对象"""
    return pygame.font.SysFont(font_list, size)


def main():
    parser = argparse.ArgumentParser(description="Monitoring Dashboard")
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_EXPORTER_URL,
        help="Prometheus Exporter metrics URL (default: %(default)s)",
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Start in fullscreen mode",
    )
    parser.add_argument(
        "--show-fps",
        action="store_true",
        help="Display FPS counter on screen",
    )
    args = parser.parse_args()

    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # Initialize pygame and print available fonts
    print("Available fonts:")
    fonts = pygame.font.get_fonts()
    for name in fonts:
        print(name)

    pygame.init()
    pygame.display.set_caption("Monitoring Dashboard")
    if args.fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    else:
        screen = pygame.display.set_mode((800, 480))

    clock = pygame.time.Clock()
    running = True
    dt = 0

    font_normal = get_font(normal_fonts, 12)
    font_mono = get_font(monospace_fonts, 12)
    font_chinese = get_font(chinese_fonts, 12)

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill((0, 0, 0))

        if args.show_fps:
            # 获取FPS
            fps = clock.get_fps()
            fps_text = font_mono.render(f"{fps:.0f}", True, (0, 255, 0))
            # 绘制到左上角
            screen.blit(fps_text, (4, 4))

        # flip() the display to put your work on screen
        pygame.display.flip()
        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    pygame.quit()

    # root = tk.Tk()
    # if args.fullscreen:
    #     root.attributes("-fullscreen", True)
    #     root.config(cursor="none")
    # app = MonitoringDashboardApp(root, exporter_url=args.url)
    # app.mainloop()


if __name__ == "__main__":
    main()
