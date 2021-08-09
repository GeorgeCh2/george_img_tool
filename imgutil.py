import io
import argparse
import pyexif
import colorsys
import piexif
from PIL import Image, ImageCms, ExifTags
from pyheif_pillow_opener import register_heif_opener

Format = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/heic": "HEIC"
}

Ext_Format = {
    "jpg": "JPEG",
    "png": "PNG",
    "heic": "HEIC",
    "HEIC": "HEIC"
}

OrientationDict = {
    "Horizontal (normal)": "1",
    "Mirror horizontal": "2",
    "Rotate 180": "3",
    "Mirror vertical": "4",
    "Mirror horizontal and rotate 270 CW": "5",
    "Rotate 90 CW": "6",
    "Mirror horizontal and rotate 90 CW": "7",
    "Rotate 270 CW": "8"
}


def get_dominant_color(image):
    # 颜色模式转换，以便输出rgb颜色值
    image = image.convert('RGBA')

    if image.size[0] > 300 or image.size[1] > 300:
        # 生成缩略图，减少计算量，减小cpu压力
        image.thumbnail((200, 200))

    max_score = 0
    color_count = 0
    dominant_color = None
    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        # rgb 转为 hsv（h:色调、s:饱和度、v:明度），比 RGB 更接近人们对彩色的感知经验
        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1] + 0.1

        # Calculate the score, preferring highly saturated colors.
        # Add 0.1 to the saturation so we don't completely ignore grayscale
        # colors by multiplying the count by zero, but still give them a low
        # weight.
        score = saturation * count
        if score > max_score:
            max_score = score
            color_count = score / (saturation * 10)
            dominant_color = (r, g, b)
    return (color_count * 10) / (image.size[0] * image.size[1]), dominant_color


def convert_to_srgb(img):
    """
    convert to sRGB if image contain 'icc_profile'
    :param img:
    :return:
    """
    # get icc profile from img info
    icc = img.info.get('icc_profile', '')
    if icc:
        # convert to sRGB
        io_handle = io.BytesIO(icc)
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img


def save_image(img, output, quality=None, icc_profile=None):
    """
    保存图片
    :param img:         图片数据
    :param output:      输出路径
    :param quality:     编码质量
    :param icc_profile: icc 文件
    :return:
    """
    # get image format by FileName suffix
    out_path = output.split('.')
    img_format = Ext_Format[out_path[-1]]
    if img_format is None:
        print("The output %s format is not support.", output)
        return

    # 保存为 JPEG 格式时，统一先转为 RGB
    if img_format == 'JPEG':
        img = img.convert('RGB')
    img.save(output, format=img_format, quality=quality if quality else ''.encode(),
             icc_profile=icc_profile if icc_profile else ''.encode())


def fit_size(src_size, dst_size):
    max_src_size = max(src_size[0], src_size[1])
    min_src_size = min(src_size[0], src_size[1])
    max_dst_size = max(dst_size[0], dst_size[1])
    min_dst_size = min(dst_size[0], dst_size[1])

    out_width = src_size[0]
    out_height = src_size[1]
    if max_src_size > max_dst_size or min_src_size > min_dst_size:
        src_aspect = src_size[0] / src_size[1]
        dst_aspect = dst_size[0] / dst_size[1]

        if src_aspect > dst_aspect:
            if max_src_size > max_dst_size:
                out_width = max_dst_size
                out_height = round(out_width / src_aspect)
        else:
            if src_aspect >= 1 and src_size[1] > min_dst_size:
                out_height = min_dst_size
                out_width = round(out_height * src_aspect)
            elif src_aspect < 1 and src_size[0] > min_dst_size:
                out_width = min_dst_size
                out_height = round(out_width / src_aspect)

    out_width = (out_width >> 1) << 1
    out_height = (out_height >> 1) << 1

    return out_width, out_height


def main(arguments):
    register_heif_opener()

    # get image info
    if arguments.exifinfo:
        try:
            img = Image.open(arguments.input)
        except IOError as ex:
            print("read img failed %s"%ex)
            img = None

        exif_editor = pyexif.ExifEditor(arguments.input)
        exif = exif_editor.getDictTags()

        # width & height
        if img:
            print('width|{0}'.format(img.size[0]))
            print('height|{0}'.format(img.size[1]))
        else:
            print('width|{0}'.format(exif['ImageWidth']))
            print('height|{0}'.format(exif['ImageHeight']))

        # exif
        if exif is not None:
            if 'DateTimeOriginal' in exif.keys():
                print('DateTimeOriginal|{0}'.format(exif['DateTimeOriginal']))

            if 'Orientation' in exif.keys():
                # heif 图片如果宽高是已旋转之后的，就不用返回该值
                if img is None:
                    print('orientation|{0}'.format(OrientationDict[exif['Orientation']]))

            if 'GPSLatitudeRef' in exif.keys():
                print('latiR|{0}'.format(exif['GPSLatitudeRef']))

            if 'GPSLatitude' in exif.keys():
                print('lati|{0}'.format(exif['GPSLatitude']))

            if 'GPSLongitudeRef' in exif.keys():
                print('longR|{0}'.format(exif['GPSLongitudeRef']))

            if 'GPSLongitude' in exif.keys():
                print('long|{0}'.format(exif['GPSLongitude']))

            if 'GPSAltitudeRef' in exif.keys():
                print('altiR|{0}'.format(exif['GPSAltitudeRef']))

            if 'GPSAltitude' in exif.keys():
                print('alti|{0}'.format(exif['GPSAltitude']))

        print("success")
        return

    # remove gps
    if arguments.rmgps:
        exif_editor = pyexif.ExifEditor(arguments.input)
        exif_dict = {"GPSLatitudeRef": "", "GPSLatitude": "", "GPSLongitudeRef": "", "GPSLongitude": "",
                     "GPSAltitudeRef": "", "GPSAltitude": "", "GPSAreaInformation": ""}
        exif_editor.setTags(exif_dict)
        print("remove gps info success")
        return

    if arguments.dominantcolor:
        try:
            img = Image.open(arguments.input)
        except IOError:
            print("read img failed")
            img = None
        proportion, color = get_dominant_color(img)
        print("dominantColor|{0}".format(color))
        print("proportion|{0}".format(proportion))
        return

    # open image
    try:
        img = Image.open(arguments.input)
    except IOError:
        print("Can't load %s", arguments.input)
        return

    # convert to sRGB if contain iccProfile
    img_convert = convert_to_srgb(img)
    if img.info.get('icc_profile', '') != img_convert.info.get('icc_profile', ''):
        img_icc_profile = img_convert.info.get('icc_profile', '')
    else:
        img_icc_profile = None

    # rotate
    if arguments.rotate:
        exif_editor = pyexif.ExifEditor(arguments.input)
        exif = exif_editor.getDictTags()
        if exif is not None:
            # find orientation in exif
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    orientation_val = exif.get(orientation)
                    if orientation_val:
                        if orientation_val == 2:
                            img_convert = img_convert.transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation_val == 3:
                            img_convert = img_convert.rotate(180, expand=True)
                        elif orientation_val == 4:
                            img_convert = img_convert.rotate(180, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation_val == 5:
                            img_convert = img_convert.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation_val == 6:
                            img_convert = img_convert.rotate(-90, expand=True)
                        elif orientation_val == 7:
                            img_convert = img_convert.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation_val == 8:
                            img_convert = img_convert.rotate(90, expand=True)

                        del exif[orientation]
                        break

    # resize
    if arguments.resize:
        # 输出路径以及对应的尺寸 {'out.jpg':'1600x1600'}
        size_dict = eval(arguments.resize)
        for output, size in size_dict.items():
            size_arr = size.split('x')
            out_size = list(int(x) for x in size_arr)
            fit_out_size = fit_size(img.size, out_size)
            print("resize image to w {0} and h {1}".format(fit_out_size[0], fit_out_size[1]))
            # resize
            img_out = img_convert.resize((fit_out_size[0], fit_out_size[1]), Image.ANTIALIAS)

            # crop
            if arguments.crop:
                left = (img_out.size[0] - out_size[0]) / 2
                right = left + out_size[0]
                upper = (img_out.size[1] - out_size[1]) / 2
                lower = upper + out_size[1]
                img_out = img_out.crop((left, upper, right, lower))

            save_image(img_out, output, arguments.quality, img_icc_profile)
        print('resize img success.')
        return

    if arguments.output:
        save_image(img_convert, arguments.output, arguments.quality, img_icc_profile)
        print("success")


if __name__ == "__main__":
    # parse arg
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='The path of input picture', type=str)
    parser.add_argument('-exifinfo', action='store_true', help='Get the image info', default=False)
    parser.add_argument('-dominantcolor', action='store_true', help='Get the image dominant color', default=False)
    parser.add_argument('-rotate', action='store_true', help='Rotate the image', default=False)
    parser.add_argument('-rmgps', action='store_true', help="remove gps of the exif", default=False)
    parser.add_argument('-quality', help='the quality of encode image', default=None, type=int)
    parser.add_argument('-resize', help='resize the image', type=str, default=None)
    parser.add_argument('-crop', action='store_true', help='crop the image', default=False)
    parser.add_argument('-o', '--output', help='The path of output picture', type=str)
    args = parser.parse_args()

    main(args)
