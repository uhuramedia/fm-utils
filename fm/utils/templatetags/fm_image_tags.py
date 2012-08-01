# -*- coding: utf-8 -*-
import re
import logging
import os
import requests
import hashlib
import subprocess
try:
    import Image
except ImportError:
    from PIL import Image

from django import template
from django.conf import settings

from fm.utils.image import scale_and_crop

register = template.Library()


@register.simple_tag
def image_scale(image, width, height, upscale=True, crop=False, center=True):
    try:
        if type(image) == unicode and image.startswith("http:"):
            # image is HTTP URL
            path = image
        else:
            # image is Django object
            path = image.path

        # determine format, extensions
        if path.lower().endswith('png'):
            img_format, extension = "PNG", "png"
        else:
            img_format, extension = "JPEG", "jpg"
        suffix = '-%dx%d.%s' % (width, height, extension)
        exp = re.compile('\.(png|jpg|jpeg|gif)$', re.IGNORECASE)

        if type(image) == unicode and image.startswith("http:"):
            # hash filename
            filename = hashlib.md5(image).hexdigest() + "." + extension
            # construct paths + urls where image + scaled version would be
            path = os.path.join(settings.MEDIA_ROOT, 'downloaded_cache', filename)
            media_url = settings.MEDIA_URL + 'downloaded_cache/' + filename
            scale_path = exp.sub(suffix, path)
            scale_url = exp.sub(suffix, media_url)
            # check if scaled version already there
            if os.path.exists(scale_path):
                return scale_url
            # check if at least original already downloaded
            if not os.path.exists(path):
                # download if it does not exist
                r = requests.get(image, timeout=1.0)
                out_file = open(path, "wb")
                out_file.write(r.content)
                out_file.close()
        else:
            # work normally with Django image object
            scale_path = exp.sub(suffix, path)
            scale_url = exp.sub(suffix, image.url)
            path = image.path
            # check if scaled version already there
            if os.path.exists(scale_path):
                return scale_url

        # open with PIL to convert
        im = Image.open(path)
        if img_format == "JPEG" and im.mode != "RGB":
            # convert JPEGs to RGB to be safe
            im = im.convert("RGB")
        if img_format == "PNG":
            # copy PNG info from original
            # http://stackoverflow.com/a/1233807/62421
            png_info = im.info
            # do not sharpen PNGs, might look worse instead of better
            im = scale_and_crop(im, width, height, upscale, crop, center, sharpen=False)
            im.save(scale_path, img_format, quality=90, **png_info)
        else:
            im = scale_and_crop(im, width, height, upscale, crop, center)
            im.save(scale_path, img_format, quality=90)

        # optimize if jpegtran/pngout is installed
        # when your JPEG image is under 10K, it’s better to be saved as baseline JPEG (estimated 75% chance it will be smaller)
        # for files over 10K the progressive JPEG will give you a better compression (in 94% of the cases)
        # http://www.yuiblog.com/blog/2008/12/05/imageopt-4/
        # for png use pngout
        # http://www.codinghorror.com/blog/2007/03/getting-the-most-out-of-png.html
        try:
            # do not print output from console
            fnull = open(os.devnull, 'w')
            if img_format == "JPEG":
                if os.path.getsize(scale_path) > 10000:
                    result = subprocess.call(["jpegtran", "-copy", "none", "-optimize", "-progressive", "-outfile", scale_path, scale_path], stdout=fnull, stderr=fnull)
                else:
                    result = subprocess.call(["jpegtran", "-copy", "none", "-optimize", "-outfile", scale_path, scale_path], stdout=fnull, stderr=fnull)
            elif img_format == "PNG":
                result = subprocess.call(["pngout", scale_path], stdout=fnull, stderr=fnull)
        except OSError:
            pass
        finally:
            fnull.close()

        return scale_url
    except Exception, e:
        logging.error(str(e))
