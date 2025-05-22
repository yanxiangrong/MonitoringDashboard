def blend_color(fg, bg, alpha):
    """fg, bg: (r, g, b), alpha: 0~1"""
    return tuple(int(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb
