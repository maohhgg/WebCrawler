from PIL import Image, ImageFilter
import os


class graphic:
    def __init__(self, image=None):
        self.im = image

    def gaussian_blur(self, radius):
        self.im = self.im.filter(MyGaussianBlur(radius))
        return self

    def save(self, name):
        if self.im:
            self.im.save(name)

        return self

    def open(self, name):
        if os.path.isfile(name):
            self.im = Image.open(name)

        return self

    def merge(self, image, args=None, option=None):
        if args is None:
            args = [0, 0]
        if image and self.im:
            p = list(image.size)
            q = list(self.im.size)
            l = int((q[0] - p[0]) / 2)
            h = int((q[1] - p[1]) / 2)
            box = (l, h, l + p[0], h + p[1])
            self.im.paste(image, box)
        return self

    def center_cut(self, width=None, height=None):
        if not width:
            width = self.im.size[0]
        if not height:
            height = self.im.size[1]
        p = [width, height]
        q = list(self.im.size)
        l = int((q[0] - p[0]) / 2)
        h = int((q[1] - p[1]) / 2)
        box = (l, h, l + p[0], h + p[1])
        return self.im.crop(box)

    def new(self, imgSize=(0, 0), imgMode='RGB', bgColor=(0, 0, 0)):
        self.im = Image.new(imgMode, imgSize, bgColor)
        return self

    def resize(self, width=None, height=None):
        p = self.im.size
        if not width:
            width = int(height / (p[1] / p[0]))
        if not height:
            height = int(width / (p[0] / p[1]))

        self.im = self.im.resize((width, height), Image.ANTIALIAS)
        return self

    def get_image(self):
        return self.im


class MyGaussianBlur(ImageFilter.Filter):

    def __init__(self, radius=2, bounds=None):
        self.radius = radius
        self.bounds = bounds

    def filter(self, image):
        if self.bounds:
            clips = image.crop(self.bounds).gaussian_blur(self.radius)
            image.paste(clips, self.bounds)
            return image
        else:
            return image.gaussian_blur(self.radius)
