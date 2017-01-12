from PIL import Image, ImageDraw


def rgb2hsv(r, g, b):
    R = r / 255.0
    G = g / 255.0
    B = b / 255.0
    cmax = max(R, G, B)
    cmin = min(R, G, B)
    delta = cmax - cmin
    H, S, V = 0, 0, 0
    if delta == 0:
        H = 0
    elif cmax == R:
        H = 60 * (((G - B) / delta) % 6)
    elif cmax == G:
        H = 60 * ((B - R) / delta + 2)
    elif cmax == B:
        H = 60 * ((R - G) / delta + 4)
    if cmax == 0:
        S = 0
    else:
        S = delta / cmax
    V = cmax
    return H, S, V


def thres(pil_Image):
    """ Thresholding the image
    """
    w, h = pil_Image.size
    thim = Image.new("RGB", (w, h))
    thdr = ImageDraw.Draw(thim)
    PX = pil_Image.load()
    # make threshold image
    for x in range(0, w):
        for y in range(0, h):
            r, g, b = PX[x, y][:3]
            hsv = rgb2hsv(r, g, b)
            if hsv[2] > 0.9 and hsv[1] < 0.1:
                thdr.point([x, y], fill=(0, 0, 0))
            else:
                thdr.point([x, y], fill=(255, 255, 255))
    thim.show()
    return thim
