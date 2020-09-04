# -*- coding: utf-8 -*-
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class CaptchaImages(object):
    # 随机生成验证码图片背景颜色
    def back_random_color(self, is_light=True):
        return (random.randint(0, 127) + int(is_light) * 128, random.randint(0, 127) + int(is_light) * 128,
                random.randint(0, 127) + int(is_light) * 128)

    # 获取随机颜色
    def get_random_color(self):
        c1 = random.randint(50, 150)
        c2 = random.randint(50, 150)
        c3 = random.randint(50, 150)
        return c1, c2, c3

    # 用来随机生成一个字符串
    def gene_text(self, number):
        # 生成52个大小写英文字母
        source = list(string.ascii_letters)
        # 添加上数字
        for index in range(0, 10):
            source.append(str(index))
        return ''.join(random.sample(source, number))  # number是生成验证码的位数

    # 用来绘制干扰线
    def gene_line(self, draw, width, height, linecolor):
        # random.randint(a, b)用于生成一个指定范围内的证书，其中第一个参数a是上限，第二个参数b是下限，生成的随机数n：a<=n<=b
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        # 在图像上画线，参数值为线的起始和终止位置坐标[(x, y), (x, y)]和线的填充颜色
        draw.line([begin, end], fill=linecolor)

    def gene_point(self, draw, width, height, linecolor):
        # random.randint(a, b)用于生成一个指定范围内的证书，其中第一个参数a是上限，第二个参数b是下限，生成的随机数n：a<=n<=b
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        # 在图像上画线，参数值为线的起始和终止位置坐标[(x, y), (x, y)]和线的填充颜色
        draw.point([begin, end], fill=linecolor)

    # 生成验证码
    def gene_code(self, size, bgcolor, font_path, number, draw_line, fontcolor, line_number, linecolor):
        # 宽和高
        width, height = size
        # 创建图片, 'RGBA'表示4*8位像素，真彩+透明通道
        image = Image.new('RGBA', (width, height), bgcolor)
        # 验证码的字体。ImageFont这个函数从指定的文件加载了一个字体对象，并且为指定大小的字体创建了字体对象。
        font = ImageFont.truetype(font_path, 70)
        # 创建画笔，创建可用于绘制给定图像的对象
        draw = ImageDraw.Draw(image)
        # 随机生成想要的字符串
        text = self.gene_text(number)
        # 返回给定文本的宽度和高度，返回值为2元组
        font_width, font_height = font.getsize(text)
        # 填充字符串,参数分别是：文本的左上角坐标，文本内容，字体，文本的填充颜色
        draw.text(((width - font_width) / number, (height - font_height) / number), text, font=font, fill=fontcolor)

        if draw_line:
            # 计算要画的线的条数
            line_count = random.randint(line_number[0], line_number[1])
            # print('line_count = ', line_count)
            for i in range(line_count):
                self.gene_line(draw, width, height, linecolor)
            for i in range(500):
                self.gene_point(draw, width, height, self.get_random_color())
        # 创建扭曲，transform(size, method, data) 其中第一个参数是尺寸大小， Image.AFFINE表示仿射变化
        # 第三个参数是转换方法的额外数据， Image.BILINEAR是线性插值法
        image = image.transform((width + 20, height + 10), Image.AFFINE, (1, -0.3, 0, -0.1, 1, 0), Image.BILINEAR)
        # 滤镜，边界加强，ImageFilter.EDGE_ENHANCE_MORE为深度边缘增强滤波，会使得图像中边缘部分更加明显。
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        # 保存验证码图片
        # image.save('idencode.png')
        stream = BytesIO()
        image.save(stream, format="png")
        image.seek(0)
        return text, stream.getvalue()

    def get_image(self):
        # 字体的位置
        # font_path = r'fonts\actionj.ttf'
        font_path = random.choice(
            [
                r'C:\Users\Administrator\Desktop\myself\FlaskCode\ihome_flask\ihome\utlis\captcha\fonts\actionj.ttf',
                r'C:\Users\Administrator\Desktop\myself\FlaskCode\ihome_flask\ihome\utlis\captcha\fonts\Arial.ttf',
                r'C:\Users\Administrator\Desktop\myself\FlaskCode\ihome_flask\ihome\utlis\captcha\fonts\Georgia.ttf'
            ]
        )
        # 生成几位数的验证码
        number = 4
        # 生成验证码图片的高度和宽度
        size = (200, 75)
        # 背景颜色，默认为白色
        # bgcolor = (255, 255, 255)
        bgcolor = self.back_random_color()
        # 字体颜色，默认为蓝色
        # fontcolor = (0, 0, 255)
        fontcolor = self.get_random_color()
        # 干扰线颜色，默认为红色
        # linecolor = (255, 0, 0)
        linecolor = self.get_random_color()
        # 是否加入干扰线
        draw_line = True
        # 假如干扰线条数的上/下限
        line_number = (8, 20)
        # 调用生成验证码diamante
        text, image = self.gene_code(size, bgcolor, font_path, number, draw_line, fontcolor, line_number, linecolor)
        # print(text, image)
        return text, image

    def captcha(self):
        return self.get_image()


captcha = CaptchaImages()

# if __name__ == '__main__':
#     print(captcha.captcha())
#     a = VerifyImages()
#     print(a.get_image())
