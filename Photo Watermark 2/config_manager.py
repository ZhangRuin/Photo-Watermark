import os
import json
import shutil

class ConfigManager:
    def __init__(self):
        # 获取应用数据目录
        self.app_data_dir = self._get_app_data_directory()
        # 配置文件路径
        self.config_file = os.path.join(self.app_data_dir, "config.json")
        # 模板文件夹
        self.templates_dir = os.path.join(self.app_data_dir, "templates")
        
        # 确保目录存在
        self._ensure_directories()
    
    def _get_app_data_directory(self):
        """获取应用数据目录"""
        if os.name == 'nt':  # Windows
            app_data = os.getenv('APPDATA')
            return os.path.join(app_data, "PhotoWatermark")
        else:  # macOS, Linux
            home = os.path.expanduser("~")
            return os.path.join(home, ".photo_watermark")
    
    def _ensure_directories(self):
        """确保配置目录存在"""
        try:
            if not os.path.exists(self.app_data_dir):
                os.makedirs(self.app_data_dir)
            if not os.path.exists(self.templates_dir):
                os.makedirs(self.templates_dir)
        except Exception as e:
            print(f"创建配置目录失败: {str(e)}")
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
        return self._get_default_config()
    
    def save_config(self, config):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "watermark_text": "水印文本",
            "opacity": 50,
            "position": [0.5, 0.5],
            "export_format": "JPEG",
            "naming_rule": "original",
            "prefix": "wm_",
            "suffix": "_watermarked"
        }
    
    def save_template(self, template_name, template_data):
        """保存水印模板"""
        try:
            # 验证模板名称
            if not self._is_valid_template_name(template_name):
                raise ValueError("无效的模板名称")
            
            # 保存模板文件
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
            return False
    
    def load_template(self, template_name):
        """加载水印模板"""
        try:
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载模板失败: {str(e)}")
        return None
    
    def delete_template(self, template_name):
        """删除水印模板"""
        try:
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            if os.path.exists(template_file):
                os.remove(template_file)
                return True
        except Exception as e:
            print(f"删除模板失败: {str(e)}")
        return False
    
    def get_templates(self):
        """获取所有可用模板"""
        templates = {}
        try:
            if os.path.exists(self.templates_dir):
                for filename in os.listdir(self.templates_dir):
                    if filename.endswith('.json'):
                        template_name = filename[:-5]  # 移除.json后缀
                        template_data = self.load_template(template_name)
                        if template_data:
                            templates[template_name] = template_data
        except Exception as e:
            print(f"获取模板列表失败: {str(e)}")
        return templates
    
    def rename_template(self, old_name, new_name):
        """重命名水印模板"""
        try:
            # 验证新名称
            if not self._is_valid_template_name(new_name):
                raise ValueError("无效的模板名称")
            
            # 检查新名称是否已存在
            new_template_file = os.path.join(self.templates_dir, f"{new_name}.json")
            if os.path.exists(new_template_file):
                raise ValueError("模板名称已存在")
            
            # 重命名文件
            old_template_file = os.path.join(self.templates_dir, f"{old_name}.json")
            if os.path.exists(old_template_file):
                shutil.move(old_template_file, new_template_file)
                return True
        except Exception as e:
            print(f"重命名模板失败: {str(e)}")
        return False
    
    def _is_valid_template_name(self, name):
        """验证模板名称是否有效"""
        if not name or len(name) > 50:
            return False
        
        # 检查是否包含非法字符
        illegal_chars = '<>"/\\|?*:\n\t'
        for char in illegal_chars:
            if char in name:
                return False
        
        # 检查是否为保留文件名
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if name.upper() in reserved_names:
            return False
        
        return True
    
    def export_template(self, template_name, export_path):
        """导出模板到文件"""
        try:
            template_data = self.load_template(template_name)
            if template_data:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, ensure_ascii=False, indent=2)
                return True
        except Exception as e:
            print(f"导出模板失败: {str(e)}")
        return False
    
    def import_template(self, import_path, template_name=None):
        """从文件导入模板"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # 如果没有指定名称，使用文件名
            if template_name is None:
                template_name = os.path.splitext(os.path.basename(import_path))[0]
                
            # 确保名称有效，如果无效则添加后缀
            counter = 1
            base_name = template_name
            while not self._is_valid_template_name(template_name) or os.path.exists(os.path.join(self.templates_dir, f"{template_name}.json")):
                template_name = f"{base_name}_{counter}"
                counter += 1
            
            return self.save_template(template_name, template_data)
        except Exception as e:
            print(f"导入模板失败: {str(e)}")
        return False
    
    def reset_config(self):
        """重置配置到默认值"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            return True
        except Exception as e:
            print(f"重置配置失败: {str(e)}")
        return False
    
    def backup_config(self, backup_path=None):
        """备份配置"""
        try:
            if backup_path is None:
                # 默认备份路径
                backup_path = os.path.join(self.app_data_dir, "config_backup.json")
            
            if os.path.exists(self.config_file):
                shutil.copy2(self.config_file, backup_path)
                return True
        except Exception as e:
            print(f"备份配置失败: {str(e)}")
        return False
    
    def restore_config(self, backup_path=None):
        """从备份恢复配置"""
        try:
            if backup_path is None:
                # 默认备份路径
                backup_path = os.path.join(self.app_data_dir, "config_backup.json")
            
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.config_file)
                return True
        except Exception as e:
            print(f"恢复配置失败: {str(e)}")
        return False