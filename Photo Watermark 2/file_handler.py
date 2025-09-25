import os
from PIL import Image
import tkinter as tk

class FileHandler:
    def __init__(self):
        # 支持的图片格式
        self.supported_formats = {
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
        }
        
        # 输出格式映射
        self.output_formats = {
            'jpeg': ('JPEG', '.jpg'),
            'png': ('PNG', '.png')
        }
    
    def validate_image(self, file_path):
        """验证单个图片文件是否有效"""
        if not os.path.exists(file_path):
            return False
        
        # 检查文件扩展名
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.supported_formats:
            return False
        
        # 尝试打开图片以验证其有效性
        try:
            with Image.open(file_path) as img:
                img.verify()  # 验证图片的有效性
            return True
        except Exception:
            return False
    
    def validate_images(self, file_paths):
        """批量验证图片文件"""
        valid_images = []
        for file_path in file_paths:
            if self.validate_image(file_path):
                valid_images.append(file_path)
        return valid_images
    
    def get_image_files_from_folder(self, folder_path):
        """从文件夹中获取所有有效的图片文件"""
        image_files = []
        
        if not os.path.isdir(folder_path):
            return image_files
        
        # 遍历文件夹
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.validate_image(file_path):
                    image_files.append(file_path)
        
        return image_files
    
    def get_drop_files(self, event):
        """获取拖拽到窗口的文件列表"""
        # 处理Windows和MacOS的拖拽
        if hasattr(event, 'data'):
            # MacOS风格的拖拽
            data = event.data
            # 处理多个文件的情况
            if data.startswith('file://'):
                paths = []
                # 分割多个文件路径
                for path in data.split(' '):
                    if path.startswith('file://'):
                        # 移除file://前缀并解码URL编码的字符
                        import urllib.parse
                        local_path = urllib.parse.unquote(path[7:])
                        paths.append(local_path)
                return paths
        
        # Windows风格的拖拽
        # 在Windows上，Tkinter的拖拽事件处理可能需要特殊处理
        # 这里使用clipboard的方式尝试获取拖拽的文件
        try:
            # 尝试从剪贴板获取拖拽的文件
            # 注意：这只是一个基本实现，实际效果可能因系统而异
            root = event.widget.winfo_toplevel()
            root.clipboard_clear()
            # 这里可能需要特定平台的代码来获取拖拽文件
            return []
        except Exception:
            return []
    
    def ensure_directory_exists(self, directory_path):
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path)
                return True
            except Exception:
                return False
        return True
    
    def get_safe_filename(self, filename):
        """获取安全的文件名，移除或替换非法字符"""
        # Windows文件名非法字符
        illegal_chars = '<>"/\\|?*:\n\t'
        safe_filename = filename
        for char in illegal_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 移除控制字符
        safe_filename = ''.join(char for char in safe_filename if ord(char) >= 32)
        
        # 限制文件名长度
        if len(safe_filename) > 200:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:200-len(ext)] + ext
        
        return safe_filename
    
    def get_unique_filename(self, directory, filename):
        """获取唯一的文件名，如果文件已存在则添加数字后缀"""
        if not os.path.exists(os.path.join(directory, filename)):
            return filename
        
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while os.path.exists(os.path.join(directory, f"{name}_{counter}{ext}")):
            counter += 1
        
        return f"{name}_{counter}{ext}"