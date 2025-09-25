import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import shutil
from pathlib import Path

class PhotoWatermarkTool:
    def __init__(self, root):
        self.root = root
        self.root.title("照片水印工具")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # 设置中文字体
        self.style = ttk.Style()
        
        # 支持的图片格式
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        self.output_formats = ['.jpg', '.png']
        
        # 存储已导入的图片
        self.images = []
        self.current_image_index = -1
        
        # 创建界面
        self.create_widgets()
        
        # 绑定拖拽事件
        self.bind_drag_and_drop()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 导入按钮
        import_btn = ttk.Button(control_frame, text="导入图片", command=self.import_images)
        import_btn.pack(fill=tk.X, pady=5)
        
        import_folder_btn = ttk.Button(control_frame, text="导入文件夹", command=self.import_folder)
        import_folder_btn.pack(fill=tk.X, pady=5)
        
        ttk.Separator(control_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # 导出设置
        export_frame = ttk.LabelFrame(control_frame, text="导出设置", padding="10")
        export_frame.pack(fill=tk.X, pady=5)
        
        # 输出格式选择
        ttk.Label(export_frame, text="输出格式:").pack(anchor=tk.W, pady=2)
        self.output_format_var = tk.StringVar(value=".jpg")
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X)
        
        ttk.Radiobutton(format_frame, text="JPEG (.jpg)", variable=self.output_format_var, value=".jpg").pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="PNG (.png)", variable=self.output_format_var, value=".png").pack(anchor=tk.W)
        
        # 文件命名规则
        ttk.Label(export_frame, text="文件命名规则:").pack(anchor=tk.W, pady=2)
        self.naming_rule_var = tk.StringVar(value="original")
        naming_frame = ttk.Frame(export_frame)
        naming_frame.pack(fill=tk.X)
        
        ttk.Radiobutton(naming_frame, text="保留原文件名", variable=self.naming_rule_var, value="original").pack(anchor=tk.W)
        
        # 前缀设置
        prefix_frame = ttk.Frame(naming_frame)
        prefix_frame.pack(fill=tk.X, padx=20)
        ttk.Radiobutton(prefix_frame, text="添加前缀:", variable=self.naming_rule_var, value="prefix").pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar(value="wm_")
        ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=10).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 后缀设置
        suffix_frame = ttk.Frame(naming_frame)
        suffix_frame.pack(fill=tk.X, padx=20)
        ttk.Radiobutton(suffix_frame, text="添加后缀:", variable=self.naming_rule_var, value="suffix").pack(side=tk.LEFT)
        self.suffix_var = tk.StringVar(value="_watermarked")
        ttk.Entry(suffix_frame, textvariable=self.suffix_var, width=10).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 导出按钮
        export_btn = ttk.Button(control_frame, text="导出图片", command=self.export_images)
        export_btn.pack(fill=tk.X, pady=5)
        
        # 中间预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="10")
        preview_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_canvas = tk.Canvas(preview_frame, bg="#f0f0f0", cursor="crosshair")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 底部图片列表
        list_frame = ttk.LabelFrame(main_frame, text="图片列表", padding="10")
        list_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # 创建水平滚动条
        self.horizontal_scroll = ttk.Scrollbar(list_frame, orient="horizontal")
        self.horizontal_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建Canvas作为滚动区域
        self.canvas = tk.Canvas(list_frame, xscrollcommand=self.horizontal_scroll.set, height=150)
        self.canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        # 配置滚动条
        self.horizontal_scroll.config(command=self.canvas.xview)
        
        # 在Canvas上创建Frame用于放置图片
        self.image_list_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.image_list_frame, anchor="nw")
        
        # 绑定配置事件
        self.image_list_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # 绑定鼠标滚轮事件以支持水平滚动
        self.image_list_frame.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def bind_drag_and_drop(self):
        # 注意：标准Tkinter对文件拖拽的支持有限
        # 这里只是一个占位函数，实际的拖拽功能在Windows上需要使用额外的库
        # 例如pywin32或者tkinterdnd2
        pass
    
    # 注释掉不支持的拖拽相关函数
    # def on_drag_enter(self, event):
    #     pass
    # 
    # def on_drag_leave(self, event):
    #     pass
    # 
    # def on_drop(self, event):
    #     pass
    # 
    # def get_drop_files(self, data):
    #     pass
    
    def import_images(self):
        # 打开文件选择对话框
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("BMP文件", "*.bmp"),
                ("TIFF文件", "*.tiff *.tif"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            self.process_imported_files(file_paths)
    
    def import_folder(self):
        # 打开文件夹选择对话框
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        
        if folder_path:
            file_paths = []
            # 遍历文件夹中的所有图片文件
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in self.supported_formats:
                        file_paths.append(os.path.join(root, file))
            
            if file_paths:
                self.process_imported_files(file_paths)
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")
    
    def process_imported_files(self, file_paths):
        # 处理导入的文件
        new_images = []
        for file_path in file_paths:
            try:
                # 检查文件扩展名
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in self.supported_formats:
                    continue
                
                # 检查是否已导入
                if not any(img['path'] == file_path for img in self.images):
                    # 打开图片获取基本信息
                    with Image.open(file_path) as img:
                        width, height = img.size
                    
                    # 添加到图片列表
                    image_info = {
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'width': width,
                        'height': height,
                        'original_path': os.path.dirname(file_path)
                    }
                    new_images.append(image_info)
            except Exception as e:
                print(f"导入文件 {file_path} 失败: {str(e)}")
        
        if new_images:
            # 更新图片列表
            self.images.extend(new_images)
            # 更新界面显示
            self.update_image_list()
            # 默认显示第一张图片
            if self.current_image_index == -1 and self.images:
                self.show_image(0)
            
            messagebox.showinfo("导入成功", f"成功导入 {len(new_images)} 张图片")
    
    def update_image_list(self):
        # 清空现有列表
        for widget in self.image_list_frame.winfo_children():
            widget.destroy()
        
        # 创建新的图片项
        for i, image_info in enumerate(self.images):
            item_frame = ttk.Frame(self.image_list_frame, padding="5")
            item_frame.pack(side=tk.LEFT, padx=5)
            
            # 创建缩略图
            try:
                with Image.open(image_info['path']) as img:
                    img.thumbnail((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    
                    # 创建图片按钮
                    img_btn = ttk.Button(item_frame, image=photo, command=lambda idx=i: self.show_image(idx))
                    img_btn.image = photo  # 保持引用
                    img_btn.pack()
                    
                    # 添加文件名标签
                    name_label = ttk.Label(item_frame, text=image_info['name'], wraplength=100)
                    name_label.pack()
                    
                    # 如果是当前选中的图片，添加高亮
                    if i == self.current_image_index:
                        item_frame.config(relief=tk.SUNKEN, borderwidth=2)
                    # 存储索引以便后续更新
                    item_frame.image_index = i
            except Exception as e:
                print(f"创建缩略图失败: {str(e)}")
                
    def highlight_selected_image(self, index):
        # 只更新选中状态，不重建整个列表
        for widget in self.image_list_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and hasattr(widget, 'image_index'):
                if widget.image_index == index:
                    widget.config(relief=tk.SUNKEN, borderwidth=2)
                else:
                    widget.config(relief=tk.FLAT, borderwidth=1)
    
    def show_image(self, index):
        # 显示指定索引的图片
        if 0 <= index < len(self.images):
            self.current_image_index = index
            image_info = self.images[index]
            
            try:
                # 打开图片
                with Image.open(image_info['path']) as img:
                    # 调整图片大小以适应预览窗口
                    canvas_width = self.preview_canvas.winfo_width() - 20
                    canvas_height = self.preview_canvas.winfo_height() - 20
                    
                    # 避免在预览窗口还未完全初始化时计算尺寸
                    if canvas_width <= 0 or canvas_height <= 0:
                        canvas_width, canvas_height = 800, 600
                    
                    img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    
                    # 创建 PhotoImage 对象
                    self.preview_photo = ImageTk.PhotoImage(img)
                    
                    # 在画布上显示图片
                    self.preview_canvas.delete("all")
                    x = (canvas_width - img.width) // 2
                    y = (canvas_height - img.height) // 2
                    self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
                    
                    # 更新窗口标题
                    self.root.title(f"照片水印工具 - {image_info['name']}")
                    
                    # 移除对update_image_list的调用，避免递归
                    # 更新选中状态但不重建整个列表
                    self.highlight_selected_image(index)
            except Exception as e:
                messagebox.showerror("错误", f"显示图片失败: {str(e)}")
    
    def on_mousewheel(self, event):
        # 处理鼠标滚轮事件，支持水平滚动
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
    
    def on_frame_configure(self, event):
        # 更新Canvas的滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        # 当Canvas大小改变时，更新内部窗口
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def export_images(self):
        # 导出图片
        if not self.images:
            messagebox.showinfo("提示", "请先导入图片")
            return
        
        # 选择导出文件夹
        export_folder = filedialog.askdirectory(title="选择导出文件夹")
        if not export_folder:
            return
        
        # 检查是否与任何原始文件夹相同
        for image_info in self.images:
            if os.path.normpath(export_folder) == os.path.normpath(image_info['original_path']):
                response = messagebox.askyesno("警告", "导出文件夹与原始图片所在文件夹相同，可能会覆盖原文件。是否继续？")
                if not response:
                    return
                break
        
        # 导出设置
        output_format = self.output_format_var.get()
        naming_rule = self.naming_rule_var.get()
        
        # 开始导出
        success_count = 0
        for image_info in self.images:
            try:
                # 生成输出文件名
                base_name = os.path.splitext(image_info['name'])[0]
                if naming_rule == "prefix":
                    output_name = f"{self.prefix_var.get()}{base_name}{output_format}"
                elif naming_rule == "suffix":
                    output_name = f"{base_name}{self.suffix_var.get()}{output_format}"
                else:  # original
                    output_name = f"{base_name}{output_format}"
                
                output_path = os.path.join(export_folder, output_name)
                
                # 复制文件（在实际应用中，这里应该是添加水印后的处理）
                # 目前只是简单复制，后续会添加水印处理逻辑
                with Image.open(image_info['path']) as img:
                    # 根据输出格式保存
                    if output_format.lower() == ".jpg":
                        # JPEG不支持透明度，需要将RGBA转换为RGB
                        if img.mode == 'RGBA':
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            # 将RGBA图片粘贴到白色背景上
                            background.paste(img, mask=img.split()[3])  # 使用Alpha通道作为掩码
                            background.save(output_path, format="JPEG", quality=95)
                        else:
                            img.save(output_path, format="JPEG", quality=95)
                    else:
                        img.save(output_path, format="PNG")
                
                success_count += 1
            except Exception as e:
                print(f"导出文件 {image_info['name']} 失败: {str(e)}")
        
        # 显示完整的导出信息，包括可点击的路径
        messagebox.showinfo("导出完成", 
                           f"成功导出 {success_count} 张图片\n" 
                           f"导出位置: {export_folder}\n" 
                           f"请在文件资源管理器中导航到此路径查看导出的图片")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoWatermarkTool(root)
    
    # 监听窗口大小变化，更新预览图片
    # 使用一个字典来存储resize_flag状态
    resize_state = {'flag': False}
    
    def on_resize(event):
        if app.current_image_index >= 0 and not resize_state['flag']:
            resize_state['flag'] = True
            # 使用after来延迟调用，避免频繁更新
            root.after(100, update_image_after_resize)
    
    def update_image_after_resize():
        if app.current_image_index >= 0:
            app.show_image(app.current_image_index)
        resize_state['flag'] = False
    
    root.bind("<Configure>", on_resize)
    
    root.mainloop()