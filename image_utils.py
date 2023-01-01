import math
from pathlib import Path
from typing import Union, Tuple, Literal, List
from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_image(path: Path):
    return Image.open(path)


def load_font(path: Union[str, Path], size: int, variation: str = None):
    if isinstance(path, Path):
        path = str(path)
    font = ImageFont.truetype(path, size)
    if variation:
        font.set_variation_by_name(variation)
    return font


class PMImage:
    def __init__(self,
                 image: Union[Image.Image, Path] = None,
                 *,
                 size: Tuple[int, int] = (200, 200),
                 color: Union[str, Tuple[int, int, int, int]] = (255, 255, 255, 255),
                 mode: Literal["1", "CMYK", "F", "HSV", "I", "L", "LAB", "P", "RGB", "RGBA", "RGBX", "YCbCr"] = 'RGBA'
                 ):
        """
        初始化图像，优先读取image参数，如无则新建图像
            :param image: PIL对象或图像路径
            :param size: 图像大小
            :param color: 图像颜色
            :param mode: 图像模式
        """
        if image:
            self.image = load_image(image) if isinstance(image, Path) else image.copy()
        else:
            if mode == 'RGB':
                color = (color[0], color[1], color[2])
            self.image = Image.new(mode, size, color)
        self.draw = ImageDraw.Draw(self.image)

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    @property
    def size(self) -> Tuple[int, int]:
        return self.image.size

    @property
    def mode(self) -> str:
        return self.image.mode

    def show(self) -> None:
        self.image.show()

    def convert(self, mode: str):
        self.image = self.image.convert(mode)
        self.draw = ImageDraw.Draw(self.image)

    def save(self, path: Union[str, Path], **kwargs):
        """
        保存图像
            :param path: 保存路径
        """
        self.image.save(path, **kwargs)

    def text_length(self, text: str, font: ImageFont.ImageFont) -> int:
        return int(self.draw.textlength(text, font))

    def text_size(self, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
        return self.draw.textsize(text, font)

    @staticmethod
    def text_box_height(text: str,
                        width: Tuple[int, int],
                        height: Tuple[int, int],
                        font: ImageFont.ImageFont = None) -> int:
        text_height = font.getsize(text)[1]
        width_now = width[0]
        height_now = height[0]
        for c in text:
            if c in ['.', '。'] and width_now == width[0] and c == text[-1]:
                continue
            if c == '^':
                width_now = width[0]
                height_now += text_height
                continue
            c_length = font.getsize(c)[0]
            if width_now == width[0] and height_now >= height[1]:
                break
            if width_now + c_length > width[1]:
                width_now = width[0]
                height_now += text_height
            else:
                width_now += c_length
        return height_now

    def resize(self, size: Union[float, Tuple[int, int]]):
        """
        缩放图片
        :param size: 缩放大小/区域
        """
        if isinstance(size, (float, int)):
            self.image = self.image.resize((int(self.width * size), int(self.height * size)), Image.LANCZOS)
        else:
            self.image = self.image.resize(size, Image.LANCZOS)
        self.draw = ImageDraw.Draw(self.image)

    def crop(self, box: Tuple[int, int, int, int]):
        """
        裁剪图像
        :param box: 目标区域
        """
        self.image = self.image.crop(box)
        self.draw = ImageDraw.Draw(self.image)

    def rotate(self, angle: float, expand: bool = False, **kwargs):
        """
        旋转图像
        :param angle: 角度
        :param expand: expand
        """
        self.image.rotate(angle, resample=Image.BICUBIC, expand=expand, **kwargs)
        self.draw = ImageDraw.Draw(self.image)

    def paste(self,
              image: Union[Image.Image, 'PMImage', Path],
              pos: Tuple[int, int],
              alpha: bool = True,
              ):
        """
        粘贴图像
        :param image: 图像
        :param pos: 位置
        :param alpha: 是否透明
        """
        if image is None:
            return
        if isinstance(image, Path):
            image = load_image(image)
        if isinstance(image, PMImage):
            image = image.image
        if alpha:
            image = image.convert('RGBA')
            self.image.alpha_composite(image, pos)
        else:
            self.image.paste(image, pos)
        self.draw = ImageDraw.Draw(self.image)

    def text(self,
             text: str,
             width: Union[float, Tuple[float, float]],
             height: Union[float, Tuple[float, float]],
             font: ImageFont.ImageFont = None,
             color: Union[str, Tuple[int, int, int, int]] = 'white',
             align: Literal['left', 'center', 'right'] = 'left'
             ):
        """
        写文本
            :param text: 文本
            :param width: 位置横坐标
            :param height: 位置纵坐标
            :param font: 字体
            :param color: 颜色
            :param align: 对齐类型
        """
        if align == 'left':
            if isinstance(width, tuple):
                width = width[0]
            if isinstance(height, tuple):
                height = height[0]
            self.draw.text((width, height), text, color, font)
        elif align in ['center', 'right']:
            w, h = self.draw.textsize(text, font)
            if align == 'center':
                w = width[0] + (width[1] - width[0] - w) / 2 if isinstance(width, tuple) else width
                h = height[0] + (height[1] - height[0] - h) / 2 if isinstance(height, tuple) else height
            else:
                if isinstance(width, tuple):
                    width = width[1]
                w = width - w
                h = height[0] if isinstance(height, tuple) else height
            self.draw.text((w, h),
                           text,
                           color,
                           font)
        else:
            raise ValueError('对齐类型必须为\'left\', \'center\'或\'right\'')

    def text_box(self,
                 text: str,
                 width: Tuple[int, int],
                 height: Tuple[int, int],
                 font: ImageFont.ImageFont = None,
                 color: Union[str, Tuple[int, int, int, int]] = 'white'):
        text_height = font.getsize(text)[1]
        width_now = width[0]
        height_now = height[0]
        for c in text:
            if c in ['.', '。'] and width_now == width[0] and c == text[-1]:
                continue
            if c == '^':
                width_now = width[0]
                height_now += text_height
                continue
            c_length = font.getsize(c)[0]
            if width_now == width[0] and height_now >= height[1]:
                break
            self.draw.text((width_now, height_now), c, color, font=font)
            if width_now + c_length > width[1]:
                width_now = width[0]
                height_now += text_height
            else:
                width_now += c_length
        height_now += text_height
        return height_now - height[0]

    # def text_box_extra(self,
    #                    text: str,
    #                    width1: Tuple[int, int],
    #                    width2: Tuple[int, int],
    #                    height1: Tuple[int, int],
    #                    height2: Tuple[int, int],
    #                    font: ImageFont.ImageFont = None,
    #                    color: Union[str, Tuple[int, int, int, int]] = 'white'):
    #     flag = False
    #     text_height = font.getsize(text)[1]
    #     width, height = width1, height1
    #     width_now = width[0]
    #     height_now = height[0]
    #     for c in text:
    #         if c == '^':
    #             width_now = width[0]
    #             height_now += text_height
    #             continue
    #         c_length = font.getsize(c)[0]
    #         if width_now == width[0] and height_now >= height[1]:
    #             if flag:
    #                 break
    #             flag = True
    #             width, height = width2, height2
    #             width_now = width[0]
    #             # height_now = height[0]
    #             # continue
    #         self.draw.text((width_now, height_now), c, color, font=font)
    #         if width_now + c_length > width[1]:
    #             width_now = width[0]
    #             height_now += text_height
    #         else:
    #             width_now += c_length
    #     return height_now - height[0]

    def stretch(self,
                pos: Tuple[int, int],
                length: int,
                type: Literal['width', 'height'] = 'height'):
        """
        将某一部分进行拉伸
        :param pos: 拉伸的部分
        :param length: 拉伸的目标长/宽度
        :param type: 拉伸方向，width:横向, height: 竖向
        """
        if pos[0] <= 0:
            raise ValueError('起始轴必须大于等于0')
        if pos[1] <= pos[0]:
            raise ValueError('结束轴必须大于起始轴')
        if type == 'height':
            if pos[1] >= self.height:
                raise ValueError('终止轴必须小于图片高度')
            top = self.image.crop((0, 0, self.width, pos[0]))
            bottom = self.image.crop((0, pos[1], self.width, self.height))
            if length == 0:
                self.image = Image.new('RGBA', (self.width, top.height + bottom.height))
                self.image.paste(top, (0, 0))
                self.image.paste(bottom, (0, top.height))
            else:
                center = self.image.crop((0, pos[0], self.width, pos[1])).resize((self.width, length),
                                                                                 Image.LANCZOS)
                self.image = Image.new('RGBA', (self.width, top.height + center.height + bottom.height))
                self.image.paste(top, (0, 0))
                self.image.paste(center, (0, top.height))
                self.image.paste(bottom, (0, top.height + center.height))
            self.draw = ImageDraw.Draw(self.image)
        elif type == 'width':
            if pos[1] >= self.width:
                raise ValueError('终止轴必须小于图片宽度')
            top = self.image.crop((0, 0, pos[0], self.height))
            bottom = self.image.crop((pos[1], 0, self.width, self.height))
            if length == 0:
                self.image = Image.new('RGBA', (top.width + bottom.width, self.height))
                self.image.paste(top, (0, 0))
                self.image.paste(bottom, (top.width, 0))
            else:
                center = self.image.crop((pos[0], 0, pos[1], self.height)).resize((length, self.height),
                                                                                  Image.LANCZOS)
                self.image = Image.new('RGBA', (top.width + center.width + bottom.width, self.height))
                self.image.paste(top, (0, 0))
                self.image.paste(center, (top.width, 0))
                self.image.paste(bottom, (top.width + center.width, 0))
            self.draw = ImageDraw.Draw(self.image)
        else:
            raise ValueError('类型必须为\'width\'或\'height\'')

    def draw_rectangle(self,
                       pos: Tuple[int, int, int, int],
                       color: Union[str, Tuple[int, int, int, int]] = 'white',
                       width: int = 1):
        """
        绘制矩形
        :param pos: 位置
        :param color: 颜色
        :param width: 宽度
        """
        self.draw.rectangle(pos, color, width=width)

    def draw_circle(self,
                    pos: tuple,
                    color: Union[str, Tuple[int, int, int, int]] = 'white',
                    width: int = 1):
        self.draw.ellipse(pos, fill=color, width=width)

    def draw_rounded_rectangle(self,
                               pos: Tuple[int, int, int, int],
                               radius: int = 5,
                               color: Union[str, Tuple[int, int, int, int]] = 'white',
                               width: int = 1):
        """
        绘制圆角矩形
        :param pos: 圆角矩形的位置
        :param radius: 半径
        :param color: 颜色
        :param width: 宽度
        """
        self.convert("RGBA")
        self.draw.rounded_rectangle(xy=pos, radius=radius, fill=color, width=width)

    def draw_rounded_rectangle2(self,
                                pos: Tuple[int, int],
                                size: Tuple[int, int],
                                radius: int = 5,
                                color: Union[str, Tuple[int, int, int, int]] = 'white',
                                angles: List[Literal['ul', 'ur', 'll', 'lr']] = None):
        """
        选择最多4个角绘制圆角矩形
        :param pos: 左上角起点坐标
        :param size: 矩形大小
        :param radius: 半径
        :param color: 颜色
        :param angles: 角列表
        :return:
        """
        self.draw.rectangle((pos[0] + radius / 2, pos[1], pos[0] + size[0] - (radius / 2), pos[1] + size[1]),
                            fill=color)
        self.draw.rectangle((pos[0], pos[1] + radius / 2, pos[0] + size[0], pos[1] + size[1] - (radius / 2)),
                            fill=color)
        angle_pos = {
            'ul': (pos[0], pos[1], pos[0] + radius, pos[1] + radius),
            'ur': (pos[0] + size[0] - radius, pos[1], pos[0] + size[0], pos[1] + radius),
            'll': (pos[0], pos[1] + size[1] - radius, pos[0] + radius, pos[1] + size[1]),
            'lr': (pos[0] + size[0] - radius, pos[1] + size[1] - radius, pos[0] + size[0], pos[1] + size[1]),
        }
        for angle, pos2 in angle_pos.items():
            if angle in angles:
                self.draw.ellipse(pos2, fill=color)
            else:
                self.draw.rectangle(pos2, fill=color)

    def draw_line(self,
                  begin: Tuple[int, int],
                  end: Tuple[int, int],
                  color: Union[str, Tuple[int, int, int, int]] = 'black',
                  width: int = 1):
        """
        画线
        :param begin: 起始点
        :param end: 终点
        :param color: 颜色
        :param width: 宽度
        :return:
        """
        self.draw.line(begin + end, fill=color, width=width)

    def to_circle(self, shape: str = 'rectangle'):
        """
        将图片转换为圆形
        """
        self.convert('RGBA')
        w, h = self.size
        r2 = min(w, h)
        if w != h:
            self.image.resize((r2, r2), Image.LANCZOS)
        if shape == 'circle':
            mask = Image.new('RGBA', (r2, r2), (255, 255, 255, 0))
            pi = self.image.load()
            pim = mask.load()
            for i in range(r2):
                for j in range(r2):
                    lx = abs(i - r2 // 2)
                    ly = abs(j - r2 // 2)
                    l = (pow(lx, 2) + pow(ly, 2)) ** 0.5
                    if l < r2 // 2:
                        pim[i, j] = pi[i, j]
            self.image = mask
        else:
            width = 1
            antialias = 4
            ellipse_box = [0, 0, r2 - 2, r2 - 2]
            mask = Image.new(
                size=(int(self.image.width * antialias), int(self.image.height * antialias)),
                mode="L",
                color="black")
            draw = ImageDraw.Draw(mask)
            for offset, fill in (width / -2.0, "black"), (width / 2.0, "white"):
                left, top = [(value + offset) * antialias for value in ellipse_box[:2]]
                right, bottom = [(value - offset) * antialias for value in ellipse_box[2:]]
                draw.ellipse([left, top, right, bottom], fill=fill)
            mask = mask.resize(self.image.size, Image.LANCZOS)
            self.image.putalpha(mask)

        self.draw = ImageDraw.Draw(self.image)

    def to_rounded_corner(self, radii: int = 30):
        """
        将图片变为圆角
            :param radii: 半径
        """
        circle = Image.new("L", (radii * 2, radii * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)
        self.convert("RGBA")
        w, h = self.image.size
        alpha = Image.new("L", self.image.size, 255)
        alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))
        alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))
        alpha.paste(
            circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii)
        )
        alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))
        self.image.putalpha(alpha)
        self.draw = ImageDraw.Draw(self.image)

    def add_border(self, border_size: int = 10, color: Union[str, Tuple[int, int, int, int]] = 'black',
                   shape: str = 'rectangle'):
        """
        给图片添加边框
            :param border_size: 边框宽度
            :param color: 边框颜色
            :param shape: 边框形状，rectangle或circle
        """
        self.convert("RGBA")
        if shape == 'circle':
            new_img = Image.new('RGBA', (self.width + border_size, self.height + border_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(new_img)
            draw.ellipse((0, 0, self.width + border_size, self.height + border_size), fill=color)
            new_img.alpha_composite(self.image, (border_size // 2, border_size // 2))
            self.image = new_img
            self.draw = ImageDraw.Draw(self.image)
        elif shape == 'rectangle':
            self.image = ImageOps.expand(self.image, border=border_size, fill=color)
            self.draw = ImageDraw.Draw(self.image)

    def add_background(self, background: Union[Image.Image, "PMImage"], pos: Tuple[int, int]):
        """
        添加背景
            :param background: 背景图片
            :param pos: 背景图片位置
        """
        if isinstance(background, PMImage):
            background = background.image
        background.alpha_composite(self.image, pos)
        self.image = background
        self.draw = ImageDraw.Draw(self.image)

    def covered(self, image: Union[Path, Image.Image, "PMImage"]):
        """
        使用image图案进行填满
            :param image: 图案
        """
        if isinstance(image, Path):
            image = load_image(image)
        elif isinstance(image, PMImage):
            image = image.image

        width_center = int(self.width / 2)
        height_center = int(self.height / 2)
        width_num = math.ceil(width_center / image.width)
        height_num = math.ceil(height_center / image.height)
        # self.image.alpha_composite(image, (width_center, height_center))
        for i in range(width_num + 1):
            for j in range(height_num + 1):
                if i != 0:
                    self.image.alpha_composite(image, (width_center - i * image.width, height_center - j * image.height))
                if j != 0:
                    self.image.alpha_composite(image,(width_center + i * image.width, height_center - j * image.height))
                    self.image.alpha_composite(image, (width_center + i * image.width, height_center + j * image.height))
                    if i != 0:
                        self.image.alpha_composite(image, (width_center - i * image.width, height_center + j * image.height))
                if j == 0:
                    self.image.alpha_composite(image, (width_center + i * image.width, height_center + j * image.height))
