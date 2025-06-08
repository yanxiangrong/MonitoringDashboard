import argparse

import pygame

from config import DEFAULT_EXPORTER_URL


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

    # Initialize pygame and print available fonts
    print("Available fonts:")
    fonts = pygame.font.get_fonts()
    for name in fonts:
        print(name)

    pygame.init()
    screen = pygame.display.set_mode(
        (800, 480), pygame.FULLSCREEN if args.fullscreen else 0
    )
    pygame.display.set_caption("Monitoring Dashboard")

    clock = pygame.time.Clock()
    running = True
    dt = 0

    # font = pygame.font.SysFont("pibotolt", 12)  # If only english characters are needed
    font = pygame.font.SysFont("wenquanyizenhei", 12)

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
            fps_text = font.render(f"{fps:.0f}", True, (0, 255, 0))
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
