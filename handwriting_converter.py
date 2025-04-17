import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
import tkinter.font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from datetime import datetime
import random
import json

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=20, padding=8, bg='#6c5ce7', fg='white', hover_bg='#a29bfe', **kwargs):
        # 获取父窗口的背景色
        parent_bg = '#f5f6fa'  # 使用固定的背景色
        super().__init__(parent, borderwidth=0, highlightthickness=0, bg=parent_bg)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.radius = radius
        self.padding = padding
        
        # 创建按钮文本
        self.text = text
        self.font = ('微软雅黑', 11)
        
        # 绑定事件
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        
        # 初始绘制
        self._draw()
        
    def _draw(self, color=None):
        self.delete('all')
        if color is None:
            color = self.bg
            
        # 获取文本尺寸
        text_width = len(self.text) * 12
        text_height = 24
        
        # 计算按钮尺寸
        width = text_width + self.padding * 4
        height = text_height + self.padding * 2
        
        # 创建圆角矩形路径
        self.create_rounded_rect(0, 0, width, height, self.radius, color)
        
        # 添加文本
        self.create_text(width/2, height/2, text=self.text, fill=self.fg, font=self.font)
        
        # 设置画布尺寸
        self.configure(width=width, height=height)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        # 创建更平滑的圆角矩形
        points = []
        # 右上角
        points.extend([x2-radius, y1])
        points.extend([x2, y1])
        points.extend([x2, y1+radius])
        # 右下角
        points.extend([x2, y2-radius])
        points.extend([x2, y2])
        points.extend([x2-radius, y2])
        # 左下角
        points.extend([x1+radius, y2])
        points.extend([x1, y2])
        points.extend([x1, y2-radius])
        # 左上角
        points.extend([x1, y1+radius])
        points.extend([x1, y1])
        points.extend([x1+radius, y1])
        
        # 使用smooth=True创建平滑的圆角
        return self.create_polygon(points, smooth=True, fill=color)
        
    def _on_enter(self, event):
        self._draw(self.hover_bg)
        
    def _on_leave(self, event):
        self._draw(self.bg)
        
    def _on_click(self, event):
        if self.command:
            self.command()

class HandwritingConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("手写模拟器")
        self.root.geometry("1400x800")  # 加宽窗口以适应更大的预览区域
        
        # 创建必要的文件夹
        self.output_dir = "Output"
        self.fonts_dir = "fonts"
        self.background_dir = "background"
        for directory in [self.output_dir, self.fonts_dir, self.background_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # 设置窗口背景色和主题色
        self.bg_color = '#f5f6fa'
        self.primary_color = '#6c5ce7'  # 更柔和的紫色
        self.secondary_color = '#a29bfe'  # 更浅的紫色
        self.text_color = '#2d3436'
        self.root.configure(bg=self.bg_color)
        
        # 初始化字体和背景
        self.init_fonts()
        self.init_background()
        self.init_text_color()
        self.init_text_spacing()
        self.init_chaos_level()
        self.init_margins()  # 初始化边距设置
        
        # 加载保存的设置
        self.load_settings()
        
        # 设置整体样式
        style = ttk.Style()
        style.configure("Custom.TLabel",
                       font=('微软雅黑', 11),
                       background=self.bg_color,
                       foreground=self.text_color)
        style.configure("Custom.TFrame",
                       background=self.bg_color)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20", style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题区域
        title_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame,
                              text="手写模拟器",
                              font=('微软雅黑', 24, 'bold'),
                              style="Custom.TLabel")
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 添加设置按钮
        settings_button = RoundedButton(title_frame,
                                      text="⚙",  # 使用齿轮图标
                                      command=self.show_settings,
                                      bg=self.primary_color,
                                      hover_bg=self.secondary_color,
                                      padding=4)  # 减小内边距使图标更紧凑
        settings_button.grid(row=0, column=1, sticky=tk.E, padx=(0, 10))
        
        # 添加设置文字标签
        settings_label = ttk.Label(title_frame,
                                 text="设置",
                                 font=('微软雅黑', 12),
                                 style="Custom.TLabel")
        settings_label.grid(row=0, column=2, sticky=tk.E, padx=(0, 10))
        
        # 配置标题框架的列权重
        title_frame.grid_columnconfigure(0, weight=1)
        
        # 左侧输入区域
        left_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 20))
        
        input_label = ttk.Label(left_frame,
                              text="请输入要转换的文字",
                              font=('微软雅黑', 12, 'bold'),
                              style="Custom.TLabel")
        input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 创建带滚动条的文本输入框
        text_frame = ttk.Frame(left_frame, style="Custom.TFrame")
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.text_input = tk.Text(text_frame,
                                height=15,  # 增加高度
                                width=50,   # 调整宽度
                                font=('微软雅黑', 12),
                                wrap=tk.CHAR,  # 改为CHAR，允许自动换行和输入空格
                                padx=15,
                                pady=15,
                                bg='white',
                                fg=self.text_color,
                                insertbackground=self.primary_color)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=scrollbar.set)
        
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 添加提示信息
        hint_label = ttk.Label(left_frame,
                             text="该软件由B站up主 秋寒枝叶落 制作，仅供学习交流\n若要反馈bug，添加新的功能或需要源码请发送邮件到2760032779@qq.com",
                             font=('微软雅黑', 10),
                             style="Custom.TLabel",
                             foreground='#666666')
        hint_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # 控制按钮区域
        control_frame = ttk.Frame(left_frame, style="Custom.TFrame")
        control_frame.grid(row=3, column=0, pady=20)
        
        # 使用新的圆角按钮
        convert_button = RoundedButton(control_frame,
                                     text="转换为手写体",
                                     command=self.convert_text,
                                     bg=self.primary_color,
                                     hover_bg=self.secondary_color)
        convert_button.grid(row=0, column=0, padx=5)
        
        preview_button = RoundedButton(control_frame,
                                     text="生成预览图片",
                                     command=self.generate_preview_image,
                                     bg=self.primary_color,
                                     hover_bg=self.secondary_color)
        preview_button.grid(row=0, column=1, padx=5)
        
        clear_button = RoundedButton(control_frame,
                                   text="清除内容",
                                   command=self.clear_text,
                                   bg=self.primary_color,
                                   hover_bg=self.secondary_color)
        clear_button.grid(row=0, column=2, padx=5)
        
        # 右侧预览区域
        right_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        preview_label = ttk.Label(right_frame,
                                text="预览效果",
                                font=('微软雅黑', 12, 'bold'),
                                style="Custom.TLabel")
        preview_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 创建预览画布容器
        preview_container = ttk.Frame(right_frame, style="Custom.TFrame")
        preview_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建垂直滚动条
        preview_scrollbar = ttk.Scrollbar(preview_container, orient="vertical")
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 创建水平滚动条
        preview_hscrollbar = ttk.Scrollbar(preview_container, orient="horizontal")
        preview_hscrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 创建带边框的预览画布
        self.preview_area = tk.Canvas(preview_container,
                                    width=800,
                                    height=800,
                                    bg='white',
                                    highlightbackground='#dfe6e9',
                                    highlightthickness=1,
                                    yscrollcommand=preview_scrollbar.set,
                                    xscrollcommand=preview_hscrollbar.set)
        self.preview_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置滚动条
        preview_scrollbar.configure(command=self.preview_area.yview)
        preview_hscrollbar.configure(command=self.preview_area.xview)
        
        # 配置网格权重
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)
        
        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            self.preview_area.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.preview_area.bind_all("<MouseWheel>", on_mousewheel)
        
        # 绑定窗口关闭事件，解除鼠标滚轮绑定
        def on_closing():
            self.preview_area.unbind_all("<MouseWheel>")
            self.root.destroy()
            
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 配置网格权重
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # 绑定事件
        self.text_input.bind('<Key>', self.on_text_change)
        
    def save_settings(self):
        """保存设置到文件"""
        settings = {
            'font_size': getattr(self, 'font_size', 36),
            'text_color': self.text_color_settings['color'],
            'text_opacity': self.text_color_settings['opacity'],
            'text_spacing': {
                'horizontal': self.text_spacing['horizontal'],
                'vertical': self.text_spacing['vertical']
            },
            'chaos_level': self.chaos_level,
            'margins': {
                'left': int(self.margins['left']),  # 确保保存为整数
                'right': int(self.margins['right']),
                'top': int(self.margins['top']),
                'bottom': int(self.margins['bottom'])
            },
            'background': {
                'current': self.background['current'],
                'color': self.background['color']
            }
        }
        
        # 如果有手写体字体，保存字体文件名
        if self.fonts['handwriting']:
            settings['handwriting_font'] = os.path.basename(self.fonts['handwriting'])
            
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            
    def load_settings(self):
        """从文件加载设置"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # 加载字体大小
                self.font_size = settings.get('font_size', 36)
                
                # 加载文字颜色设置
                self.text_color_settings['color'] = settings.get('text_color', '#000000')
                self.text_color_settings['opacity'] = settings.get('text_opacity', 1.0)
                
                # 加载文字间距
                spacing_settings = settings.get('text_spacing', {})
                self.text_spacing['horizontal'] = spacing_settings.get('horizontal', 0)
                self.text_spacing['vertical'] = spacing_settings.get('vertical', 10)
                
                # 加载字体混乱度
                self.chaos_level = settings.get('chaos_level', 5)
                
                # 加载边距设置
                margins_settings = settings.get('margins', {})
                self.margins['left'] = int(margins_settings.get('left', 50))  # 确保加载为整数
                self.margins['right'] = int(margins_settings.get('right', 50))
                self.margins['top'] = int(margins_settings.get('top', 50))
                self.margins['bottom'] = int(margins_settings.get('bottom', 50))
                
                # 加载背景设置
                bg_settings = settings.get('background', {})
                self.background['current'] = bg_settings.get('current')
                self.background['color'] = bg_settings.get('color', '#faf9de')
                
                # 加载手写体字体
                if 'handwriting_font' in settings:
                    font_path = os.path.join(self.fonts_dir, settings['handwriting_font'])
                    if os.path.exists(font_path):
                        self.fonts['handwriting'] = font_path
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
            
    def on_closing(self):
        """窗口关闭时的处理"""
        self.save_settings()  # 保存设置
        self.root.destroy()  # 关闭窗口
        
    def on_text_change(self, event=None):
        # 不再自动清除预览区域
        pass
        
    def process_text(self, draw, text, font, available_width, available_height, text_height, text_color, opacity):
        """处理文本的通用方法"""
        y = self.margins['top']
        lines = text.split('\n')
        
        # 使用一个字符的1/4宽度作为空格宽度
        char_bbox = draw.textbbox((0, 0), "字", font=font)
        space_width = (char_bbox[2] - char_bbox[0]) * 0.25  # 缩小为1/4宽度
        
        # 定义标点符号列表
        punctuation = '，。！？、；：""''（）《》【】…—'
        
        for line in lines:
            if y > available_height:
                break
            
            x = self.margins['left']
            
            # 遍历每个字符
            for char in line:
                # 获取字符宽度
                if char == ' ':
                    # 如果是空格，不绘制任何内容，只移动x坐标
                    x += space_width + self.text_spacing['horizontal']
                    continue
                
                # 获取字符的实际宽度
                char_bbox = draw.textbbox((0, 0), char, font=font)
                char_width = char_bbox[2] - char_bbox[0]
                
                # 如果是标点符号，减小占位宽度
                if char in punctuation:
                    char_width = char_width * 0.5  # 标点符号宽度减半
                
                # 检查是否需要换行
                if x + char_width > available_width - self.margins['right']:
                    # 移动到下一行
                    y += text_height + self.text_spacing['vertical']
                    x = self.margins['left']
                    
                    if y > available_height:
                        break
                
                # 添加随机偏移
                draw_x = x + self.get_random_offset(self.chaos_level)
                draw_y = y + self.get_random_offset(self.chaos_level)
                
                # 绘制字符
                draw.text((draw_x, draw_y), char, font=font, fill=text_color + hex(opacity)[2:].zfill(2))
                
                # 更新x坐标
                x += char_width + self.text_spacing['horizontal']
            
            # 移动到下一行
            y += text_height + self.text_spacing['vertical']
        
    def convert_text(self):
        text = self.text_input.get("1.0", tk.END)  # 移除.strip()保留所有空格
        if not text.strip():  # 只检查是否全是空白
            messagebox.showwarning("警告", "请输入要转换的文字！")
            return
            
        # 创建进度条窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("转换进度")
        progress_window.geometry("300x150")
        progress_window.configure(bg=self.bg_color)
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_frame = ttk.Frame(progress_window, padding="20", style="Custom.TFrame")
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        progress_label = ttk.Label(progress_frame,
                                text="正在转换文字...",
                                font=('微软雅黑', 12),
                                style="Custom.TLabel")
        progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame,
                                    length=200,
                                    mode='determinate',
                                    variable=progress_var)
        progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        def update_progress(value):
            progress_var.set(value)
            progress_window.update()
            
        try:
            if self.background['current']:
                try:
                    bg_img = Image.open(self.background['current'])
                    output_width, output_height = bg_img.size
                    if bg_img.mode == 'RGBA':
                        img = Image.new('RGBA', (output_width, output_height), color=self.background['color'])
                        img = Image.alpha_composite(img, bg_img)
                    else:
                        img = bg_img.copy()
                except Exception as e:
                    print(f"背景图片加载失败: {str(e)}")
                    output_width = output_height = 1000
                    img = Image.new('RGB', (output_width, output_height), color=self.background['color'])
            else:
                output_width = output_height = 1000
                img = Image.new('RGB', (output_width, output_height), color=self.background['color'])
            
            update_progress(10)
            
            draw = ImageDraw.Draw(img)
            font = self.get_font('handwriting', self.font_size)
            update_progress(40)
            
            # 计算文本高度
            test_bbox = draw.textbbox((0, 0), "测试", font=font)
            text_height = test_bbox[3] - test_bbox[1]
            
            # 计算可用区域
            available_width = output_width - self.margins['left'] - self.margins['right']
            available_height = output_height - self.margins['top'] - self.margins['bottom']
            
            # 设置文本颜色和透明度
            text_color = self.text_color_settings['color']
            opacity = int(self.text_color_settings['opacity'] * 255)
            
            # 处理文本
            self.process_text(draw, text, font, available_width, available_height, text_height, text_color, opacity)
            
            update_progress(80)
            
            # 保存图片
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f'handwriting_{timestamp}.png')
            img.save(filename)
            update_progress(100)
            
            progress_window.destroy()
            messagebox.showinfo("成功", f"手写体图片已保存至：{filename}")
            
            # 更新预览
            self.preview_area.delete("all")
            # 计算预览区域的最大尺寸
            max_preview_size = 800  # 预览区域的最大尺寸
            # 计算缩放比例，保持原始比例
            ratio = min(max_preview_size/output_width, max_preview_size/output_height)
            preview_width = int(output_width * ratio)
            preview_height = int(output_height * ratio)
            # 调整图片大小，保持原始比例
            preview_img = img.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)
            # 创建图片，保持原始比例
            self.preview_area.create_image(0, 0, image=photo, anchor="nw")
            self.preview_area.image = photo
            # 设置滚动区域
            self.preview_area.configure(scrollregion=self.preview_area.bbox("all"))
            # 设置预览区域大小
            self.preview_area.configure(width=max_preview_size, height=max_preview_size)
            
        except Exception as e:
            print(f"转换文字失败: {str(e)}")
            messagebox.showerror("错误", f"转换文字失败: {str(e)}")
            progress_window.destroy()
        
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.preview_area.delete("all")
                                    
    def init_fonts(self):
        """初始化字体设置"""
        self.fonts = {
            'default': 'msyh.ttc',  # 默认使用微软雅黑
            'handwriting': None      # 手写体字体，初始为None
        }
        
        # 检查fonts文件夹中的字体文件
        font_files = [f for f in os.listdir(self.fonts_dir) if f.endswith(('.ttf', '.ttc', '.otf'))]
        if font_files:
            # 如果找到字体文件，使用第一个作为手写体字体
            self.fonts['handwriting'] = os.path.join(self.fonts_dir, font_files[0])
        else:
            messagebox.showinfo("提示", "请在fonts文件夹中添加字体文件(.ttf/.ttc/.otf)")
            
    def get_font(self, font_type='default', size=36):
        """获取指定类型的字体"""
        try:
            if font_type == 'handwriting' and self.fonts['handwriting']:
                if os.path.exists(self.fonts['handwriting']):
                    return ImageFont.truetype(self.fonts['handwriting'], size)
                else:
                    print(f"手写体字体文件不存在: {self.fonts['handwriting']}")
                    return ImageFont.truetype(self.fonts['default'], size)
            else:
                return ImageFont.truetype(self.fonts['default'], size)
        except Exception as e:
            print(f"加载字体失败: {str(e)}")
            return ImageFont.load_default()
            
    def init_background(self):
        """初始化背景设置"""
        self.background = {
            'current': None,  # 当前背景
            'color': '#faf9de'  # 默认米色背景，模拟纸张颜色
        }
        
        # 检查background文件夹中的背景图片
        bg_files = [f for f in os.listdir(self.background_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if bg_files:
            self.background['current'] = os.path.join(self.background_dir, bg_files[0])
        else:
            messagebox.showinfo("提示", "请在background文件夹中添加纸张背景图片(.png/.jpg/.jpeg)")
            
    def init_text_color(self):
        """初始化文字颜色设置"""
        self.text_color_settings = {
            'color': '#000000',  # 默认黑色
            'opacity': 1.0       # 默认不透明
        }
        
    def init_text_spacing(self):
        """初始化文字间距设置"""
        self.text_spacing = {
            'horizontal': 0,  # 默认水平间距为0
            'vertical': 10    # 默认竖直间距为10
        }
        
    def init_chaos_level(self):
        """初始化字体混乱度设置"""
        self.chaos_level = 5  # 默认混乱度为5（范围1-10）
        
    def init_margins(self):
        """初始化边距设置"""
        self.margins = {
            'left': 50,    # 左边距
            'right': 50,   # 右边距
            'top': 50,     # 上边距
            'bottom': 50   # 下边距
        }
        
    def get_random_offset(self, chaos_level):
        """根据混乱度获取随机偏移量"""
        # 混乱度越高，偏移范围越大
        max_offset = chaos_level * 2
        return random.randint(-max_offset, max_offset)
        
    def generate_preview_image(self):
        text = self.text_input.get("1.0", tk.END)  # 移除.strip()保留所有空格
        if not text.strip():  # 只检查是否全是空白
            messagebox.showwarning("警告", "请先输入要转换的文字！")
            return
            
        try:
            # 如果有背景图片，使用背景图片的尺寸，否则使用默认尺寸
            if self.background['current']:
                try:
                    bg_img = Image.open(self.background['current'])
                    output_width, output_height = bg_img.size
                    if bg_img.mode == 'RGBA':
                        img = Image.new('RGBA', (output_width, output_height), color=self.background['color'])
                        img = Image.alpha_composite(img, bg_img)
                    else:
                        img = bg_img.copy()
                except Exception as e:
                    print(f"背景图片加载失败: {str(e)}")
                    output_width = output_height = 1000
                    img = Image.new('RGB', (output_width, output_height), color=self.background['color'])
            else:
                output_width = output_height = 1000
                img = Image.new('RGB', (output_width, output_height), color=self.background['color'])
                    
            draw = ImageDraw.Draw(img)
            font = self.get_font('handwriting', self.font_size)
            
            # 计算文本高度
            test_bbox = draw.textbbox((0, 0), "测试", font=font)
            text_height = test_bbox[3] - test_bbox[1]
            
            # 计算可用区域
            available_width = output_width - self.margins['left'] - self.margins['right']
            available_height = output_height - self.margins['top'] - self.margins['bottom']
            
            # 设置文本颜色和透明度
            text_color = self.text_color_settings['color']
            opacity = int(self.text_color_settings['opacity'] * 255)
            
            # 处理文本
            self.process_text(draw, text, font, available_width, available_height, text_height, text_color, opacity)
            
            # 显示预览
            self.preview_area.delete("all")
            # 计算预览区域的最大尺寸
            max_preview_size = 800  # 预览区域的最大尺寸
            # 计算缩放比例，保持原始比例
            ratio = min(max_preview_size/output_width, max_preview_size/output_height)
            preview_width = int(output_width * ratio)
            preview_height = int(output_height * ratio)
            # 调整图片大小，保持原始比例
            preview_img = img.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)
            # 创建图片，保持原始比例
            self.preview_area.create_image(0, 0, image=photo, anchor="nw")
            self.preview_area.image = photo
            # 设置滚动区域
            self.preview_area.configure(scrollregion=self.preview_area.bbox("all"))
            # 设置预览区域大小
            self.preview_area.configure(width=max_preview_size, height=max_preview_size)
            
        except Exception as e:
            print(f"生成预览图片失败: {str(e)}")
            messagebox.showerror("错误", f"生成预览图片失败: {str(e)}")

    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("400x500")
        settings_window.configure(bg=self.bg_color)
        
        # 设置窗口模态
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(settings_window, style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建画布和滚动条
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        # 创建设置选项框架
        settings_frame = ttk.Frame(canvas, padding="20", style="Custom.TFrame")
        
        # 配置画布
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 放置画布和滚动条
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 创建窗口来容纳设置框架
        canvas_frame = canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        
        # 字体设置
        font_label = ttk.Label(settings_frame,
                             text="字体设置",
                             font=('微软雅黑', 12, 'bold'),
                             style="Custom.TLabel")
        font_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 字体选择下拉框
        font_var = tk.StringVar()
        font_files = [f for f in os.listdir(self.fonts_dir) if f.endswith(('.ttf', '.ttc', '.otf'))]
        if not font_files:
            font_files = ["默认字体"]
        # 设置当前选中的字体
        if self.fonts['handwriting']:
            current_font = os.path.basename(self.fonts['handwriting'])
            if current_font in font_files:
                font_var.set(current_font)
            else:
                font_var.set(font_files[0])
        else:
            font_var.set("默认字体")
        
        font_combo = ttk.Combobox(settings_frame,
                                textvariable=font_var,
                                values=font_files,
                                state="readonly",
                                width=30)
        font_combo.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        
        # 字体大小设置
        size_label = ttk.Label(settings_frame,
                             text="字体大小",
                             font=('微软雅黑', 12, 'bold'),
                             style="Custom.TLabel")
        size_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        size_var = tk.StringVar(value=str(getattr(self, 'font_size', 36)))
        size_entry = ttk.Entry(settings_frame,
                             textvariable=size_var,
                             width=10)
        size_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 20))
        
        # 字水平间距设置
        h_spacing_label = ttk.Label(settings_frame,
                                text="字水平间距",
                                font=('微软雅黑', 12, 'bold'),
                                style="Custom.TLabel")
        h_spacing_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
        
        h_spacing_var = tk.StringVar(value=str(self.text_spacing['horizontal']))
        h_spacing_entry = ttk.Entry(settings_frame,
                                textvariable=h_spacing_var,
                                width=10)
        h_spacing_entry.grid(row=5, column=0, sticky=tk.W, pady=(0, 20))
        
        # 字竖直间距设置
        v_spacing_label = ttk.Label(settings_frame,
                                text="字竖直间距",
                                font=('微软雅黑', 12, 'bold'),
                                style="Custom.TLabel")
        v_spacing_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 10))
        
        v_spacing_var = tk.StringVar(value=str(self.text_spacing['vertical']))
        v_spacing_entry = ttk.Entry(settings_frame,
                                textvariable=v_spacing_var,
                                width=10)
        v_spacing_entry.grid(row=7, column=0, sticky=tk.W, pady=(0, 20))
        
        # 字体混乱度设置
        chaos_label = ttk.Label(settings_frame,
                              text="字体混乱度 (1-10)",
                              font=('微软雅黑', 12, 'bold'),
                              style="Custom.TLabel")
        chaos_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 10))
        
        # 使用IntVar
        chaos_var = tk.IntVar(value=self.chaos_level)
        
        # 创建显示整数值的StringVar
        chaos_display_var = tk.StringVar(value=str(self.chaos_level))
        
        # 更新显示值的函数
        def update_chaos_display(*args):
            chaos_display_var.set(str(int(chaos_var.get())))
        
        # 绑定变量变化事件
        chaos_var.trace_add("write", update_chaos_display)
        
        chaos_scale = ttk.Scale(settings_frame,
                              from_=1,
                              to=10,
                              orient=tk.HORIZONTAL,
                              length=200,
                              variable=chaos_var)
        chaos_scale.grid(row=9, column=0, sticky=tk.W, pady=(0, 20))
        
        # 添加显示当前值的标签，使用StringVar显示整数值
        chaos_value_label = ttk.Label(settings_frame,
                                    textvariable=chaos_display_var,
                                    font=('微软雅黑', 10),
                                    style="Custom.TLabel")
        chaos_value_label.grid(row=9, column=1, sticky=tk.W, padx=(10, 0))
        
        # 边距设置
        margins_label = ttk.Label(settings_frame,
                                text="边距设置",
                                font=('微软雅黑', 12, 'bold'),
                                style="Custom.TLabel")
        margins_label.grid(row=10, column=0, sticky=tk.W, pady=(0, 10))
        
        # 左边距设置
        left_margin_label = ttk.Label(settings_frame,
                                    text="左边距",
                                    font=('微软雅黑', 10),
                                    style="Custom.TLabel")
        left_margin_label.grid(row=11, column=0, sticky=tk.W, pady=(0, 5))
        
        left_margin_var = tk.StringVar(value=str(self.margins['left']))
        left_margin_entry = ttk.Entry(settings_frame,
                                    textvariable=left_margin_var,
                                    width=10)
        left_margin_entry.grid(row=11, column=1, sticky=tk.W, pady=(0, 5))
        
        # 右边距设置
        right_margin_label = ttk.Label(settings_frame,
                                     text="右边距",
                                     font=('微软雅黑', 10),
                                     style="Custom.TLabel")
        right_margin_label.grid(row=12, column=0, sticky=tk.W, pady=(0, 5))
        
        right_margin_var = tk.StringVar(value=str(self.margins['right']))
        right_margin_entry = ttk.Entry(settings_frame,
                                     textvariable=right_margin_var,
                                     width=10)
        right_margin_entry.grid(row=12, column=1, sticky=tk.W, pady=(0, 5))
        
        # 上边距设置
        top_margin_label = ttk.Label(settings_frame,
                                   text="上边距",
                                   font=('微软雅黑', 10),
                                   style="Custom.TLabel")
        top_margin_label.grid(row=13, column=0, sticky=tk.W, pady=(0, 5))
        
        top_margin_var = tk.StringVar(value=str(self.margins['top']))
        top_margin_entry = ttk.Entry(settings_frame,
                                   textvariable=top_margin_var,
                                   width=10)
        top_margin_entry.grid(row=13, column=1, sticky=tk.W, pady=(0, 5))
        
        # 下边距设置
        bottom_margin_label = ttk.Label(settings_frame,
                                      text="下边距",
                                      font=('微软雅黑', 10),
                                      style="Custom.TLabel")
        bottom_margin_label.grid(row=14, column=0, sticky=tk.W, pady=(0, 5))
        
        bottom_margin_var = tk.StringVar(value=str(self.margins['bottom']))
        bottom_margin_entry = ttk.Entry(settings_frame,
                                      textvariable=bottom_margin_var,
                                      width=10)
        bottom_margin_entry.grid(row=14, column=1, sticky=tk.W, pady=(0, 5))
        
        # 字体颜色设置
        color_label = ttk.Label(settings_frame,
                              text="字体颜色",
                              font=('微软雅黑', 12, 'bold'),
                              style="Custom.TLabel")
        color_label.grid(row=15, column=0, sticky=tk.W, pady=(0, 10))
        
        # 创建颜色选择框架
        color_frame = ttk.Frame(settings_frame, style="Custom.TFrame")
        color_frame.grid(row=16, column=0, sticky=tk.W, pady=(0, 10))
        
        # 创建颜色预览框
        color_var = tk.StringVar(value=self.text_color_settings['color'])
        color_preview = tk.Canvas(color_frame, width=30, height=30, 
                                bg=color_var.get(), highlightthickness=1)
        color_preview.grid(row=0, column=0, padx=(0, 10))
        
        # 创建颜色选择按钮
        def choose_color():
            color = tk.colorchooser.askcolor(color=color_var.get(), title="选择字体颜色")[1]
            if color:
                color_var.set(color)
                color_preview.configure(bg=color)
                # 自动保存颜色设置
                self.text_color_settings['color'] = color
                self.save_settings()
        
        color_button = RoundedButton(color_frame,
                                   text="选择颜色",
                                   command=choose_color,
                                   bg=self.primary_color,
                                   hover_bg=self.secondary_color,
                                   padding=4)
        color_button.grid(row=0, column=1)
        
        # 字体透明度设置
        opacity_label = ttk.Label(settings_frame,
                                text="字体透明度",
                                font=('微软雅黑', 12, 'bold'),
                                style="Custom.TLabel")
        opacity_label.grid(row=17, column=0, sticky=tk.W, pady=(0, 10))
        
        opacity_var = tk.StringVar(value=str(self.text_color_settings['opacity']))
        opacity_entry = ttk.Entry(settings_frame,
                                textvariable=opacity_var,
                                width=10)
        opacity_entry.grid(row=18, column=0, sticky=tk.W, pady=(0, 20))
        
        # 纸张背景设置
        bg_label = ttk.Label(settings_frame,
                           text="纸张背景",
                           font=('微软雅黑', 12, 'bold'),
                           style="Custom.TLabel")
        bg_label.grid(row=19, column=0, sticky=tk.W, pady=(0, 10))
        
        # 背景选择下拉框
        bg_var = tk.StringVar()
        bg_files = [f for f in os.listdir(self.background_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        bg_files.insert(0, "纯色背景")
        # 设置当前选中的背景
        if self.background['current']:
            current_bg = os.path.basename(self.background['current'])
            if current_bg in bg_files:
                bg_var.set(current_bg)
            else:
                bg_var.set("纯色背景")
        else:
            bg_var.set("纯色背景")
        
        bg_combo = ttk.Combobox(settings_frame,
                              textvariable=bg_var,
                              values=bg_files,
                              state="readonly",
                              width=30)
        bg_combo.grid(row=20, column=0, sticky=tk.W, pady=(0, 20))
        
        # 自动保存函数
        def auto_save(*args):
            try:
                # 更新字体设置
                if font_var.get() != "默认字体":
                    self.fonts['handwriting'] = os.path.join(self.fonts_dir, font_var.get())
                else:
                    self.fonts['handwriting'] = None
                    
                # 更新字体大小
                self.font_size = int(size_var.get())
                
                # 更新文字透明度
                self.text_color_settings['opacity'] = float(opacity_var.get())
                
                # 更新文字间距
                self.text_spacing['horizontal'] = int(h_spacing_var.get())
                self.text_spacing['vertical'] = int(v_spacing_var.get())
                
                # 更新字体混乱度
                self.chaos_level = chaos_var.get()
                
                # 更新边距设置
                self.margins['left'] = int(left_margin_var.get())
                self.margins['right'] = int(right_margin_var.get())
                self.margins['top'] = int(top_margin_var.get())
                self.margins['bottom'] = int(bottom_margin_var.get())
                
                # 更新背景设置
                if bg_var.get() != "纯色背景":
                    self.background['current'] = os.path.join(self.background_dir, bg_var.get())
                else:
                    self.background['current'] = None
                
                # 保存设置到文件
                self.save_settings()
            except ValueError:
                pass
        
        # 绑定变量跟踪
        font_var.trace_add("write", auto_save)
        size_var.trace_add("write", auto_save)
        h_spacing_var.trace_add("write", auto_save)
        v_spacing_var.trace_add("write", auto_save)
        chaos_var.trace_add("write", auto_save)
        left_margin_var.trace_add("write", auto_save)
        right_margin_var.trace_add("write", auto_save)
        top_margin_var.trace_add("write", auto_save)
        bottom_margin_var.trace_add("write", auto_save)
        opacity_var.trace_add("write", auto_save)
        bg_var.trace_add("write", auto_save)
        
        # 配置网格权重
        settings_window.grid_rowconfigure(0, weight=1)
        settings_window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # 更新画布滚动区域
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        settings_frame.bind('<Configure>', configure_scroll_region)
        
        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 绑定窗口关闭事件，解除鼠标滚轮绑定
        def on_closing():
            canvas.unbind_all("<MouseWheel>")
            settings_window.destroy()
            
        settings_window.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    root = tk.Tk()
    app = HandwritingConverter(root)
    root.mainloop() 
    