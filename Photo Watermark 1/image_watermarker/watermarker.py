#!/usr/bin/env python3
import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ExifTags
from datetime import datetime
import piexif


def get_exif_date(image_path):
    """从图片中获取拍摄日期（改进版本）"""
    try:
        # 方法1: 使用piexif库（更可靠）
        try:
            exif_dict = piexif.load(image_path)
            if "Exif" in exif_dict:
                # 检查DateTimeOriginal (36868)
                if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                    date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                    return date_str

                # 检查DateTime (306)
                if piexif.ImageIFD.DateTime in exif_dict["0th"]:
                    date_str = exif_dict["0th"][piexif.ImageIFD.DateTime].decode('utf-8')
                    return date_str
        except:
            pass

        # 方法2: 使用PIL的原始方法（备用）
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                # 检查所有可能的日期标签
                date_tags = [
                    36867,  # DateTimeOriginal
                    306,  # DateTime
                    36868  # DateTimeDigitized
                ]

                for tag in date_tags:
                    if tag in exif_data:
                        date_value = exif_data[tag]
                        if isinstance(date_value, str):
                            return date_value

                # 遍历所有EXIF标签查找日期
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, '')
                    if 'date' in tag_name.lower() or 'time' in tag_name.lower():
                        if isinstance(value, str):
                            return value

    except Exception as e:
        print(f"读取EXIF时出错: {e}")

    return None


def parse_exif_date(exif_date):
    """解析EXIF日期格式（改进版本）"""
    if not exif_date:
        return None

    try:
        # 处理不同的EXIF日期格式
        date_str = exif_date

        # 移除可能的乱码字符
        date_str = ''.join(c for c in date_str if c.isprintable())

        # 尝试不同的日期格式
        formats_to_try = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y:%m:%d",
            "%Y-%m-%d",
            "%Y/%m/%d"
        ]

        for fmt in formats_to_try:
            try:
                # 只取日期部分
                if ' ' in date_str:
                    date_part = date_str.split()[0]
                    return datetime.strptime(date_part, fmt.split()[0]).date()
                else:
                    return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

    except Exception as e:
        print(f"解析日期 '{exif_date}' 时出错: {e}")

    return None


def debug_exif_info(image_path):
    """调试函数：显示图片的所有EXIF信息"""
    print(f"\n调试 {os.path.basename(image_path)} 的EXIF信息:")

    # 使用piexif
    try:
        exif_dict = piexif.load(image_path)
        print("piexif读取的EXIF数据:")
        for ifd in exif_dict:
            if exif_dict[ifd]:  # 只显示有数据的部分
                print(f"  {ifd}:")
                for tag, value in exif_dict[ifd].items():
                    tag_name = piexif.TAGS[ifd][tag]["name"] if ifd in piexif.TAGS and tag in piexif.TAGS[ifd] else str(
                        tag)
                    try:
                        if isinstance(value, bytes):
                            value_str = value.decode('utf-8', errors='ignore')
                        else:
                            value_str = str(value)
                        print(f"    {tag_name}: {value_str}")
                    except:
                        print(f"    {tag_name}: [二进制数据]")
    except Exception as e:
        print(f"piexif调试失败: {e}")

    # 使用PIL
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                print("PIL读取的EXIF数据:")
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, str(tag))
                    print(f"  {tag_name}: {value}")
            else:
                print("PIL未找到EXIF数据")
    except Exception as e:
        print(f"PIL调试失败: {e}")


def add_watermark(image_path, watermark_text, font_size, color, position, output_path=None):
    """为图片添加水印"""
    try:
        # 打开图片
        image = Image.open(image_path)

        # 创建可绘制对象
        draw = ImageDraw.Draw(image)

        # 尝试加载字体
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # 如果找不到字体，使用默认字体
            font = ImageFont.load_default()

        # 使用textbbox方法获取文本尺寸
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 根据位置计算坐标
        if position == "center":
            x = (image.width - text_width) // 2
            y = (image.height - text_height) // 2
        elif position == "top-left":
            x = 10
            y = 10
        elif position == "top-right":
            x = image.width - text_width - 10
            y = 10
        elif position == "bottom-left":
            x = 10
            y = image.height - text_height - 10
        elif position == "bottom-right":
            x = image.width - text_width - 10
            y = image.height - text_height - 10
        else:
            x = 10
            y = 10

        # 添加水印文本
        draw.text((x, y), watermark_text, fill=color, font=font)

        # 保存图片
        image.save(output_path)

        # 返回水印信息用于输出
        return {
            'filename': os.path.basename(image_path),
            'watermark_text': watermark_text,
            'position': position,
            'font_size': font_size,
            'color': color,
            'output_path': output_path,
            'image_size': f"{image.width}x{image.height}",
            'watermark_coords': f"({x}, {y})"
        }

    except Exception as e:
        print(f"处理图片 {image_path} 时出错: {e}")
        return None


def print_watermark_info(info):
    """格式化输出水印信息到终端"""
    if info:
        print("=" * 60)
        print("水印处理信息:")
        print(f"  文件名: {info['filename']}")
        print(f"  图片尺寸: {info['image_size']}")
        print(f"  水印文字: {info['watermark_text']}")
        print(f"  水印位置: {info['position']} {info['watermark_coords']}")
        print(f"  字体大小: {info['font_size']}")
        print(f"  水印颜色: {info['color']}")
        print(f"  输出路径: {info['output_path']}")
        if 'exif_source' in info:
            print(f"  日期来源: {info['exif_source']}")
        print("=" * 60)
        print()


def process_directory(input_dir, font_size=20, color='red', position='center', debug=False):
    """处理目录中的所有图片"""
    # 创建输出目录 - 修改为在当前目录下创建 _watermark 文件夹
    output_dir = os.path.join(os.getcwd(), "_watermark")
    os.makedirs(output_dir, exist_ok=True)
    print(f"创建输出目录: {output_dir}")
    print()

    processed_count = 0
    skipped_count = 0

    # 遍历目录中的文件
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path):
            try:
                # 检查是否为图片文件
                with Image.open(file_path) as img:
                    # 调试模式：显示EXIF信息
                    if debug:
                        debug_exif_info(file_path)

                    # 获取EXIF日期信息
                    exif_date = get_exif_date(file_path)
                    if debug:
                        print(f"提取的EXIF日期: {exif_date}")

                    if exif_date:
                        parsed_date = parse_exif_date(exif_date)
                        if parsed_date:
                            watermark_text = parsed_date.strftime("%Y-%m-%d")
                            exif_source = "EXIF日期"
                        else:
                            watermark_text = "日期未知"
                            exif_source = "EXIF解析失败"
                    else:
                        # 使用文件修改日期作为备选
                        file_mtime = os.path.getmtime(file_path)
                        file_date = datetime.fromtimestamp(file_mtime).date()
                        watermark_text = file_date.strftime("%Y-%m-%d")
                        exif_source = "文件修改日期"

                    # 构建输出路径
                    name, ext = os.path.splitext(filename)
                    output_filename = f"{name}_watermarked{ext}"
                    output_path = os.path.join(output_dir, output_filename)

                    # 添加水印
                    result = add_watermark(
                        file_path,
                        watermark_text,
                        font_size,
                        color,
                        position,
                        output_path
                    )

                    if result:
                        # 添加EXIF来源信息
                        result['exif_source'] = exif_source
                        print_watermark_info(result)
                        processed_count += 1
                    else:
                        skipped_count += 1

            except IOError:
                # 不是图片文件，跳过
                print(f"跳过非图片文件: {filename}")
                skipped_count += 1
                continue
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                skipped_count += 1

    # 输出处理统计信息
    print("\n" + "=" * 60)
    print("处理完成统计:")
    print(f"  成功处理: {processed_count} 个文件")
    print(f"  跳过文件: {skipped_count} 个文件")
    print(f"  输出目录: {output_dir}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='为图片添加水印（使用EXIF日期）')
    parser.add_argument('image', help='要添加水印的图片路径或目录路径')
    parser.add_argument('--font-size', '-fs', type=int, default=20, help='字体大小')
    parser.add_argument('--color', '-c', default='white', help='水印颜色')
    parser.add_argument('--position', '-p', default='bottom-right',
                        choices=['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'],
                        help='水印位置')
    parser.add_argument('--debug', '-d', action='store_true', help='调试模式：显示EXIF信息')

    args = parser.parse_args()

    # 检查输入路径是文件还是目录
    if os.path.isdir(args.image):
        print(f"开始处理目录: {args.image}")
        print(f"字体大小: {args.font_size}, 颜色: {args.color}, 位置: {args.position}")
        print()
        process_directory(
            args.image,
            args.font_size,
            args.color,
            args.position,
            args.debug
        )
    elif os.path.isfile(args.image):
        print(f"开始处理单个文件: {args.image}")
        print(f"字体大小: {args.font_size}, 颜色: {args.color}, 位置: {args.position}")
        print()

        # 调试模式：显示EXIF信息
        if args.debug:
            debug_exif_info(args.image)

        # 获取EXIF日期信息
        exif_date = get_exif_date(args.image)
        if args.debug:
            print(f"提取的EXIF日期: {exif_date}")

        if exif_date:
            parsed_date = parse_exif_date(exif_date)
            if parsed_date:
                watermark_text = parsed_date.strftime("%Y-%m-%d")
                exif_source = "EXIF日期"
            else:
                watermark_text = "日期未知"
                exif_source = "EXIF解析失败"
        else:
            # 使用文件修改日期作为备选
            file_mtime = os.path.getmtime(args.image)
            file_date = datetime.fromtimestamp(file_mtime).date()
            watermark_text = file_date.strftime("%Y-%m-%d")
            exif_source = "文件修改日期"

        # 构建输出路径
        input_dir = os.path.dirname(args.image)
        output_dir = os.path.join(os.getcwd(), "_watermark")
        os.makedirs(output_dir, exist_ok=True)

        name, ext = os.path.splitext(os.path.basename(args.image))
        output_filename = f"{name}_watermarked{ext}"
        output_path = os.path.join(output_dir, output_filename)

        # 添加水印
        result = add_watermark(
            args.image,
            watermark_text,
            args.font_size,
            args.color,
            args.position,
            output_path
        )

        if result:
            # 添加EXIF来源信息
            result['exif_source'] = exif_source
            print_watermark_info(result)
            print(f"单个文件处理完成!")
        else:
            print(f"处理文件失败: {args.image}")

    else:
        print(f"错误: 路径 {args.image} 不存在")


if __name__ == "__main__":
    main()
