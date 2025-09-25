import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from PIL import Image, ImageTk
import json

# 导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from file_handler import FileHandler
from watermark_processor import WatermarkProcessor
from config_manager import ConfigManager

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片水印工具")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # 初始化模块
        self.file_handler = FileHandler()
        self.watermark_processor = WatermarkProcessor()
        self.config_manager = ConfigManager()
        
        # 存储变量
        self.imported_images = []
        self.current_image_index = -1
        self.preview_image = None
        self.preview_photo = None
        self.dragging_watermark = False
        self.watermark_x = 0
        self.watermark_y = 0
        # 为每个图片单独存储水印位置
        self.image_watermark_positions = {}
        
        # 先创建UI，确保所有变量都已初始化
        self.create_ui()
        
        # 然后加载配置，更新UI
        self.load_config()
        
    def create_ui(self):
        # 创建自定义样式
        style = ttk.Style()
        # 定义模板按钮样式
        style.configure("Template.TButton", font=('SimHei', 10))
        # 定义危险操作按钮样式（红色文本）
        style.configure("Danger.TButton", foreground="red", font=('SimHei', 10, 'bold'))
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 文件操作部分
        file_frame = ttk.LabelFrame(control_frame, text="文件操作", padding="5")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="导入图片", command=self.import_images).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="导入文件夹", command=self.import_folder).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="导出图片", command=self.export_images).pack(fill=tk.X, padx=5, pady=2)
        
        # 水印设置部分
        watermark_frame = ttk.LabelFrame(control_frame, text="水印设置", padding="5")
        watermark_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文本水印
        ttk.Label(watermark_frame, text="水印文本:").pack(anchor=tk.W, padx=5, pady=2)
        self.watermark_text_var = tk.StringVar(value=self.watermark_processor.watermark_text)
        ttk.Entry(watermark_frame, textvariable=self.watermark_text_var).pack(fill=tk.X, padx=5, pady=2)
        
        # 透明度
        ttk.Label(watermark_frame, text="透明度:").pack(anchor=tk.W, padx=5, pady=2)
        self.opacity_var = tk.IntVar(value=self.watermark_processor.opacity)
        opacity_scale = ttk.Scale(watermark_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.opacity_var, command=self.update_preview)
        opacity_scale.pack(fill=tk.X, padx=5, pady=2)
        self.opacity_label = ttk.Label(watermark_frame, text=f"{self.opacity_var.get()}%")
        self.opacity_label.pack(anchor=tk.W, padx=5)
        opacity_scale.bind("<Motion>", self.update_opacity_label)
        
        # 位置预设
        ttk.Label(watermark_frame, text="预设位置:").pack(anchor=tk.W, padx=5, pady=2)
        position_frame = ttk.Frame(watermark_frame)
        position_frame.pack(fill=tk.X, padx=5, pady=2)
        
        positions = [
            ("左上", (0, 0)), ("上中", (0.5, 0)), ("右上", (1, 0)),
            ("左中", (0, 0.5)), ("中心", (0.5, 0.5)), ("右中", (1, 0.5)),
            ("左下", (0, 1)), ("下中", (0.5, 1)), ("右下", (1, 1))
        ]
        
        for text, pos in positions:
            ttk.Button(position_frame, text=text, command=lambda p=pos: self.set_watermark_position(p)).pack(side=tk.LEFT, padx=2)
        
        # 导出设置
        export_frame = ttk.LabelFrame(control_frame, text="导出设置", padding="5")
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(export_frame, text="输出格式:").pack(anchor=tk.W, padx=5, pady=2)
        self.export_format_var = tk.StringVar(value="JPEG")
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.export_format_var, value="JPEG").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.export_format_var, value="PNG").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(export_frame, text="命名规则:").pack(anchor=tk.W, padx=5, pady=2)
        self.naming_rule_var = tk.StringVar(value="original")
        naming_frame = ttk.Frame(export_frame)
        naming_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Radiobutton(naming_frame, text="保留原名", variable=self.naming_rule_var, value="original").pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Frame(naming_frame).pack(fill=tk.X)
        ttk.Radiobutton(naming_frame, text="添加前缀:", variable=self.naming_rule_var, value="prefix").pack(side=tk.LEFT, padx=5)
        self.prefix_var = tk.StringVar(value="wm_")
        ttk.Entry(naming_frame, textvariable=self.prefix_var, width=10).pack(side=tk.LEFT, padx=2)
        
        ttk.Frame(naming_frame).pack(fill=tk.X)
        ttk.Radiobutton(naming_frame, text="添加后缀:", variable=self.naming_rule_var, value="suffix").pack(side=tk.LEFT, padx=5)
        self.suffix_var = tk.StringVar(value="_watermarked")
        ttk.Entry(naming_frame, textvariable=self.suffix_var, width=10).pack(side=tk.LEFT, padx=2)
        
        # 模板管理
        template_frame = ttk.LabelFrame(control_frame, text="模板管理", padding="5")
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(template_frame, text="保存当前设置为模板", command=self.save_template).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(template_frame, text="加载模板", command=self.load_template).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(template_frame, text="管理模板", command=self.manage_templates).pack(fill=tk.X, padx=5, pady=2)
        
        # 右侧预览区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 图片列表
        list_frame = ttk.LabelFrame(right_frame, text="已导入图片", padding="5")
        list_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.image_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, width=50, height=5)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 预览窗口
        preview_frame = ttk.LabelFrame(right_frame, text="预览", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg="#f0f0f0")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定拖拽事件
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # 允许拖拽导入 - 注意：Tkinter原生对文件拖拽支持有限
        # 以下代码为简化版，实际文件拖拽可能需要平台特定的实现
        # 建议用户使用导入按钮来添加文件
        # 如果需要完整的拖放支持，可能需要使用更高级的GUI库如wxPython或PyQt
    
    def load_config(self):
        """加载配置"""
        config = self.config_manager.load_config()
        if config:
            # 加载水印文本并更新UI
            watermark_text = config.get("watermark_text", "水印文本")
            self.watermark_processor.watermark_text = watermark_text
            self.watermark_text_var.set(watermark_text)
            
            # 加载透明度并更新UI
            opacity = config.get("opacity", 50)
            self.watermark_processor.opacity = opacity
            self.opacity_var.set(opacity)
            self.opacity_label.config(text=f"{opacity}%")
            
            # 加载其他配置
    
    def save_config(self):
        """保存配置"""
        # 确保先获取UI中最新的文本
        current_text = self.watermark_text_var.get()
        current_opacity = self.opacity_var.get()
        
        config = {
            "watermark_text": current_text,
            "opacity": current_opacity,
            # 保存其他配置
        }
        
        # 更新处理器中的值并保存配置
        self.watermark_processor.watermark_text = current_text
        self.watermark_processor.opacity = current_opacity
        
        self.config_manager.save_config(config)
    
    def import_images(self):
        """导入图片"""
        file_paths = filedialog.askopenfilenames(
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif")]
        )
        if file_paths:
            self.add_images(file_paths)
    
    def import_folder(self):
        """导入文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            file_paths = self.file_handler.get_image_files_from_folder(folder_path)
            if file_paths:
                self.add_images(file_paths)
    
    def add_images(self, file_paths):
        """添加图片到列表"""
        new_images = self.file_handler.validate_images(file_paths)
        for img_path in new_images:
            if img_path not in self.imported_images:
                self.imported_images.append(img_path)
                filename = os.path.basename(img_path)
                self.image_listbox.insert(tk.END, filename)
                # 为新图片初始化水印位置为中心
                self.image_watermark_positions[img_path] = (0.5, 0.5)
        
        if new_images and self.current_image_index == -1:
            self.current_image_index = 0
            self.update_preview()
    
    def on_image_select(self, event):
        """选择图片"""
        selection = self.image_listbox.curselection()
        if selection:
            self.current_image_index = selection[0]
            # 恢复当前图片的水印位置设置
            if self.current_image_index < len(self.imported_images):
                current_image_path = self.imported_images[self.current_image_index]
                if current_image_path in self.image_watermark_positions:
                    self.watermark_processor.position = self.image_watermark_positions[current_image_path]
            self.update_preview()
    
    def update_opacity_label(self, event):
        """更新透明度标签"""
        self.opacity_label.config(text=f"{self.opacity_var.get()}%")
    
    def set_watermark_position(self, position):
        """设置水印位置"""
        self.watermark_processor.position = position
        # 保存当前图片的水印位置
        if self.current_image_index < len(self.imported_images):
            current_image_path = self.imported_images[self.current_image_index]
            self.image_watermark_positions[current_image_path] = position
        self.update_preview()
    
    def update_preview(self, event=None):
        """更新预览"""
        if self.current_image_index < 0 or self.current_image_index >= len(self.imported_images):
            return
        
        # 更新水印设置，确保使用UI中最新的值
        self.watermark_processor.watermark_text = self.watermark_text_var.get()
        self.watermark_processor.opacity = self.opacity_var.get()
        self.opacity_label.config(text=f"{self.opacity_var.get()}%")
        
        # 处理预览图片
        image_path = self.imported_images[self.current_image_index]
        try:
            # 生成带水印的预览图
            preview_img = self.watermark_processor.apply_watermark_preview(image_path)
            
            # 调整大小以适应画布
            canvas_width = self.preview_canvas.winfo_width() - 20
            canvas_height = self.preview_canvas.winfo_height() - 20
            
            if canvas_width > 1 and canvas_height > 1:
                preview_img = self.watermark_processor.resize_preview(preview_img, canvas_width, canvas_height)
                
                # 转换为Tkinter可用的格式
                self.preview_photo = ImageTk.PhotoImage(preview_img)
                
                # 清除画布并显示新图片
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(
                    (canvas_width // 2) + 10,
                    (canvas_height // 2) + 10,
                    image=self.preview_photo
                )
                
                # 记录水印位置（相对于画布）
                self.watermark_x = (canvas_width // 2) + 10
                self.watermark_y = (canvas_height // 2) + 10
                
        except Exception as e:
            messagebox.showerror("错误", f"生成预览失败: {str(e)}")
    
    def on_canvas_click(self, event):
        """画布点击事件 - 检测并开始拖拽水印"""
        if self.current_image_index < 0 or self.current_image_index >= len(self.imported_images):
            return
        
        # 开始拖拽水印
        self.dragging_watermark = True
        # 记录初始点击位置
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        # 记录拖拽开始时的水印相对位置
        self.drag_start_position = self.watermark_processor.position
    
    def on_canvas_drag(self, event):
        """画布拖拽事件 - 实时更新水印位置"""
        if not self.dragging_watermark:
            return
        
        # 计算拖拽的相对偏移量
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width > 0 and canvas_height > 0:
            # 计算鼠标移动的相对距离（相对于画布大小的比例）
            delta_x = (event.x - self.drag_start_x) / canvas_width
            delta_y = (event.y - self.drag_start_y) / canvas_height
            
            # 计算新的水印位置
            new_x = self.drag_start_position[0] + delta_x
            new_y = self.drag_start_position[1] + delta_y
            
            # 限制位置在有效范围内 (0-1)
            new_x = max(0, min(new_x, 1))
            new_y = max(0, min(new_y, 1))
            
            # 更新水印位置
            self.watermark_processor.position = (new_x, new_y)
            
            # 实时更新预览
            self.update_preview()
    
    def on_canvas_release(self, event):
        """画布释放事件 - 结束拖拽并保存水印位置"""
        if not self.dragging_watermark:
            return
            
        self.dragging_watermark = False
        
        # 获取当前水印位置
        current_position = self.watermark_processor.position
        
        # 保存当前图片的水印位置
        if self.current_image_index < len(self.imported_images):
            current_image_path = self.imported_images[self.current_image_index]
            self.image_watermark_positions[current_image_path] = current_position
            
        # 重新更新预览以确保最终效果正确
        self.update_preview()
    
    def on_drag_enter(self, event):
        """拖拽进入事件"""
        event.widget.focus_set()
        return event.action
    
    def on_drag_leave(self, event):
        """拖拽离开事件"""
        return event.action
    
    def on_drop(self, event):
        """拖拽释放事件"""
        # 获取拖拽的文件路径
        file_paths = self.file_handler.get_drop_files(event)
        if file_paths:
            self.add_images(file_paths)
        return event.action
    
    def export_images(self):
        """导出图片"""
        if not self.imported_images:
            messagebox.showwarning("警告", "没有可导出的图片")
            return
        
        # 选择输出文件夹
        output_folder = filedialog.askdirectory()
        if not output_folder:
            return
        
        # 检查是否与原图在同一文件夹
        for img_path in self.imported_images:
            if os.path.dirname(img_path) == output_folder:
                messagebox.showwarning("警告", "禁止导出到原文件夹，以防止覆盖原图")
                return
        
        # 更新水印设置
        self.watermark_processor.watermark_text = self.watermark_text_var.get()
        self.watermark_processor.opacity = self.opacity_var.get()
        
        # 导出图片
        try:
            for img_path in self.imported_images:
                # 获取输出文件名
                output_filename = self.get_output_filename(img_path)
                output_path = os.path.join(output_folder, output_filename)
                
                # 为当前图片应用其保存的水印位置
                if img_path in self.image_watermark_positions:
                    self.watermark_processor.position = self.image_watermark_positions[img_path]
                else:
                    # 如果没有保存的位置，使用默认中心位置
                    self.watermark_processor.position = (0.5, 0.5)
                
                # 应用水印并保存
                format_type = self.export_format_var.get().lower()
                self.watermark_processor.apply_watermark_and_save(img_path, output_path, format_type)
            
            messagebox.showinfo("成功", "图片导出成功！")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def get_output_filename(self, original_path):
        """获取输出文件名"""
        original_name = os.path.basename(original_path)
        name_without_ext, ext = os.path.splitext(original_name)
        
        # 根据命名规则生成新文件名
        naming_rule = self.naming_rule_var.get()
        if naming_rule == "original":
            new_name = name_without_ext
        elif naming_rule == "prefix":
            new_name = f"{self.prefix_var.get()}{name_without_ext}"
        elif naming_rule == "suffix":
            new_name = f"{name_without_ext}{self.suffix_var.get()}"
        else:
            new_name = name_without_ext
        
        # 添加输出格式的扩展名
        output_ext = ".jpg" if self.export_format_var.get() == "JPEG" else ".png"
        return f"{new_name}{output_ext}"
    
    def save_template(self):
        """保存当前设置为模板"""
        template_name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if template_name:
            template = {
                "watermark_text": self.watermark_text_var.get(),
                "opacity": self.opacity_var.get(),
                "position": self.watermark_processor.position,
                # 保存其他设置
            }
            self.config_manager.save_template(template_name, template)
            messagebox.showinfo("成功", f"模板 '{template_name}' 已保存")
    
    def load_template(self):
        """加载模板 - 提供模板列表选择"""
        templates = self.config_manager.get_templates()
        if not templates:
            messagebox.showinfo("提示", "没有可用的模板")
            return
        
        # 创建模板选择对话框
        template_window = tk.Toplevel(self.root)
        template_window.title("选择模板")
        template_window.geometry("300x400")
        template_window.transient(self.root)
        template_window.grab_set()
        template_window.resizable(False, False)
        
        # 添加标签
        ttk.Label(template_window, text="请选择要加载的模板：").pack(padx=10, pady=10)
        
        # 添加滚动区域
        scroll_frame = ttk.Frame(template_window)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建内部框架
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # 定义选择函数
        def select_template(name):
            template = templates[name]
            self.watermark_text_var.set(template.get("watermark_text", ""))
            self.opacity_var.set(template.get("opacity", 50))
            self.watermark_processor.position = template.get("position", (0.5, 0.5))
            self.update_preview()
            messagebox.showinfo("成功", f"模板 '{name}' 已加载")
            template_window.destroy()
        
        # 添加模板列表按钮
        for template_name in sorted(templates.keys()):
            ttk.Button(
                inner_frame, 
                text=template_name, 
                command=lambda name=template_name: select_template(name),
                style="Template.TButton"
            ).pack(fill=tk.X, padx=5, pady=3)
        
        # 添加取消按钮
        ttk.Button(template_window, text="取消", command=template_window.destroy).pack(pady=10)
        
        # 更新滚动区域
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", on_frame_configure)
    
    def manage_templates(self):
        """管理模板 - 支持删除模板"""
        templates = self.config_manager.get_templates()
        if not templates:
            messagebox.showinfo("提示", "没有可用的模板")
            return
        
        # 创建模板管理对话框
        manage_window = tk.Toplevel(self.root)
        manage_window.title("管理模板")
        manage_window.geometry("400x400")
        manage_window.transient(self.root)
        manage_window.grab_set()
        
        # 添加标签
        ttk.Label(manage_window, text="模板列表管理：").pack(padx=10, pady=10)
        
        # 添加滚动区域
        scroll_frame = ttk.Frame(manage_window)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建内部框架
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # 刷新模板列表的函数
        def refresh_template_list():
            # 清空当前列表
            for widget in inner_frame.winfo_children():
                widget.destroy()
            
            # 重新加载模板
            nonlocal templates
            templates = self.config_manager.get_templates()
            
            if not templates:
                ttk.Label(inner_frame, text="没有可用的模板").pack(padx=10, pady=20)
                return
            
            # 添加模板列表项
            for template_name in sorted(templates.keys()):
                item_frame = ttk.Frame(inner_frame)
                item_frame.pack(fill=tk.X, padx=5, pady=3)
                
                # 显示模板名称
                ttk.Label(item_frame, text=template_name).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # 删除按钮
                ttk.Button(
                    item_frame, 
                    text="删除", 
                    command=lambda name=template_name: delete_template(name),
                    style="Danger.TButton"
                ).pack(side=tk.RIGHT, padx=5)
        
        # 删除模板函数
        def delete_template(name):
            if messagebox.askyesno("确认删除", f"确定要删除模板 '{name}' 吗？"):
                if self.config_manager.delete_template(name):
                    messagebox.showinfo("成功", f"模板 '{name}' 已删除")
                    refresh_template_list()  # 刷新列表
                else:
                    messagebox.showerror("错误", f"删除模板 '{name}' 失败")
        
        # 初始加载模板列表
        refresh_template_list()
        
        # 添加关闭按钮
        ttk.Button(manage_window, text="关闭", command=manage_window.destroy).pack(pady=10)
        
        # 更新滚动区域
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", on_frame_configure)

# 解决循环导入问题
try:
    from tkinter import simpledialog
except ImportError:
    pass

def main():
    """程序主入口"""
    root = tk.Tk()
    app = WatermarkApp(root)
    
    # 监听窗口大小变化以更新预览
    root.bind("<Configure>", app.update_preview)
    
    # 窗口关闭时保存配置
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_config(), root.destroy()))
    
    root.mainloop()

if __name__ == "__main__":
    main()