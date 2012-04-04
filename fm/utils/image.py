from PIL import Image, ImageFilter
from decimal import Decimal


def scale_and_crop(im, width, height, upscale, crop, center_y=True, sharpen=True):
    x, y = [Decimal(v) for v in im.size]
    if width:
        xr = Decimal(width)
    else:
        xr = Decimal(x * height / y)
    if height:
        yr = Decimal(height)
    else:
        yr = Decimal(y * width / x)

    if crop:
        r = max(xr / x, yr / y)
    else:
        r = min(xr / x, yr / y)

    if r < 1.0 or (r > 1.0 and upscale):
        im = im.resize((int(x * r), int(y * r)), resample=Image.ANTIALIAS)

    if crop:
        x, y = [Decimal(v) for v in im.size]
        ex, ey = (x - min(x, xr)) / 2, (y - min(y, yr)) / 2
        if center_y and (ex or ey):
            im = im.crop((int(ex), int(ey), int(x - ex), int(y - ey)))
        elif not center_y and (ex or ey):
            im = im.crop((int(ex), 0.0, int(x - ex), int(y - ey - ey)))

    if sharpen:
        fltr = ImageFilter.Kernel((3, 3),
                  (-1, -1, -1,
                   - 1, 22, -1,
                   - 1, -1, -1))
        im = im.filter(fltr)

    return im
