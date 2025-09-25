from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

class WatermarkProcessor:
    def __init__(self):
        # 默认水印设置
        self.watermark_text = "水印文本"
        self.opacity = 50  # 0-100
        self.position = (0.5, 0.5)  # 默认中心位置 (x, y) 相对坐标 0-1
        self.font_size = None  # 自动计算
        self.font_path = None  # 自动选择系统字体
        self.text_color = (255, 255, 0)  # 黄色文字，更显眼
    
    def apply_watermark_preview(self, image_path):
        """生成带水印的预览图片"""
        try:
            # 打开原图
            with Image.open(image_path) as base_image:
                # 转换为RGBA以支持透明度
                if base_image.mode != 'RGBA':
                    base_image = base_image.convert('RGBA')
                
                # 创建水印层
                watermark = self._create_watermark_layer(base_image.size)
                
                # 计算水印位置
                x, y = self._calculate_position(base_image.size, watermark.size)
                
                # 将水印粘贴到原图上
                result = Image.alpha_composite(base_image, watermark)
                
                # 返回结果（转换回RGB用于显示）
                if result.mode == 'RGBA':
                    return result.convert('RGB')
                return result
        except Exception as e:
            raise Exception(f"应用水印失败: {str(e)}")
    
    def apply_watermark_and_save(self, input_path, output_path, format_type):
        """应用水印并保存图片"""
        try:
            # 打开原图
            with Image.open(input_path) as base_image:
                # 转换为RGBA以支持透明度
                if base_image.mode != 'RGBA':
                    base_image = base_image.convert('RGBA')
                
                # 创建水印层
                watermark = self._create_watermark_layer(base_image.size)
                
                # 计算水印位置
                x, y = self._calculate_position(base_image.size, watermark.size)
                
                # 将水印粘贴到原图上
                result = Image.alpha_composite(base_image, watermark)
                
                # 保存图片
                if format_type == 'jpeg':
                    # JPEG不支持透明度，转换为RGB
                    if result.mode == 'RGBA':
                        result = result.convert('RGB')
                    result.save(output_path, format='JPEG', quality=95, subsampling=0)
                else:  # png
                    if result.mode != 'RGBA':
                        result = result.convert('RGBA')
                    result.save(output_path, format='PNG', compress_level=1)
        except Exception as e:
            raise Exception(f"保存带水印图片失败: {str(e)}")
    
    def _create_watermark_layer(self, image_size):
        """创建水印层"""
        # 创建透明背景
        watermark_layer = Image.new('RGBA', image_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 计算字体大小 - 增大字体比例
        if self.font_size is None:
            font_size = max(20, min(image_size[0], image_size[1]) // 10)
        else:
            font_size = self.font_size
        
        # 尝试加载字体
        font = self._load_font(font_size)
        
        # 处理文本换行
        wrapped_text = self._wrap_text(self.watermark_text, image_size[0] // 2, font)
        
        # 计算文本边界框
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算水印位置
        x = (image_size[0] - text_width) * self.position[0]
        y = (image_size[1] - text_height) * self.position[1]
        
        # 计算透明度
        alpha = int(255 * (self.opacity / 100))
        
        # 创建半透明文字，增强可见性
        # 先绘制黑色描边，使文字在任何背景上都更清晰可见
        stroke_width = 1
        for dx in [-stroke_width, 0, stroke_width]:
            for dy in [-stroke_width, 0, stroke_width]:
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), wrapped_text, font=font, fill=(0, 0, 0, alpha))
        # 绘制文本
        draw.text((x, y), wrapped_text, font=font, fill=(self.text_color[0], self.text_color[1], self.text_color[2], alpha))
        
        return watermark_layer
    
    def _load_font(self, font_size):
        """加载合适的字体，确保中文正常显示"""
        # 尝试加载系统字体
        try:
            # 在Windows上尝试加载中文字体
            if os.name == 'nt':
                # Windows系统字体路径
                windows_font_dir = os.path.join(os.environ.get('WINDIR', 'C:\Windows'), 'Fonts')
                
                # 尝试直接通过字体文件路径加载
                font_paths = [
                    os.path.join(windows_font_dir, 'simhei.ttf'),  # 黑体
                    os.path.join(windows_font_dir, 'msyh.ttc'),    # 微软雅黑
                    os.path.join(windows_font_dir, 'simsun.ttc'),   # 宋体
                    os.path.join(windows_font_dir, 'simkai.ttf'),   # 楷体
                ]
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            return ImageFont.truetype(font_path, font_size)
                        except:
                            continue
                
                # 再尝试字体名称方式
                font_names = [
                    'SimHei', '黑体',
                    'Microsoft YaHei', '微软雅黑',
                    'SimSun', '宋体',
                    'KaiTi', '楷体',
                    'Arial Unicode MS',
                    'Arial'
                ]
                
                for font_name in font_names:
                    try:
                        return ImageFont.truetype(font_name, font_size)
                    except:
                        continue
            else:  # 其他系统
                font_names = [
                    'Arial Unicode MS',
                    'WenQuanYi Micro Hei',
                    'Heiti TC',
                    'Arial',
                    'Helvetica'
                ]
                
                for font_name in font_names:
                    try:
                        return ImageFont.truetype(font_name, font_size)
                    except:
                        continue
            
            # 如果都失败，使用默认字体
            print("警告：无法加载中文字体，可能导致中文显示异常")
            return ImageFont.load_default()
        except Exception as e:
            print(f"加载字体时出错: {str(e)}")
            return ImageFont.load_default()
    
    def _wrap_text(self, text, max_width, font):
        """自动换行文本"""
        # 使用textwrap进行简单的换行处理
        # 注意：这只是基于字符数的粗略估计，可能不够精确
        lines = []
        for paragraph in text.split('\n'):
            # 估计每行的字符数
            avg_char_width = max_width // (font.size // 2)  # 粗略估计
            wrapped_lines = textwrap.wrap(paragraph, width=avg_char_width)
            if not wrapped_lines:
                lines.append('')
            else:
                lines.extend(wrapped_lines)
        return '\n'.join(lines)
    
    def _calculate_position(self, base_size, watermark_size):
        """计算水印的实际位置"""
        # 使用相对坐标计算实际像素位置
        x = (base_size[0] - watermark_size[0]) * self.position[0]
        y = (base_size[1] - watermark_size[1]) * self.position[1]
        
        # 确保位置在有效范围内
        x = max(0, min(x, base_size[0] - watermark_size[0]))
        y = max(0, min(y, base_size[1] - watermark_size[1]))
        
        return int(x), int(y)
    
    def resize_preview(self, image, max_width, max_height):
        """调整图片大小以适应预览窗口"""
        # 保持宽高比
        img_width, img_height = image.size
        ratio = min(max_width / img_width, max_height / img_height, 1.0)
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # 使用高质量的重采样方法
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def set_watermark_text(self, text):
        """设置水印文本"""
        self.watermark_text = text
    
    def set_opacity(self, opacity):
        """设置水印透明度"""
        # 确保透明度在0-100之间
        self.opacity = max(0, min(100, opacity))
    
    def set_position(self, position):
        """设置水印位置"""
        # 确保位置坐标在0-1之间
        x = max(0, min(1, position[0]))
        y = max(0, min(1, position[1]))
        self.position = (x, y)