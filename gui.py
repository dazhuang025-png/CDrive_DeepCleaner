#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘深度清理工具 - GUI界面
作者：克老 (Claude) @ 柏拉那工作室
日期：2026-03-01
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import humanize
from cleaner_core import CleanerCore
from config import *


class CleanerGUI:
    """C盘清理工具GUI类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # 核心清理对象
        self.cleaner = CleanerCore()
        self.scan_results = None
        self.selected_items = {}
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 获取磁盘使用情况
        self.update_disk_info()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 按钮样式
        style.configure('Primary.TButton', 
                       background=THEME_COLORS['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10)
        
        style.configure('Success.TButton',
                       background=THEME_COLORS['success'],
                       foreground='white',
                       borderwidth=0,
                       padding=10)
        
        style.configure('Danger.TButton',
                       background=THEME_COLORS['danger'],
                       foreground='white',
                       borderwidth=0,
                       padding=10)
        
        # 框架样式
        style.configure('Card.TFrame', background='white', relief='flat')
        
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部：标题和磁盘信息
        self.create_header(main_container)
        
        # 中间：扫描结果显示区域
        self.create_results_area(main_container)
        
        # 底部：操作按钮
        self.create_action_buttons(main_container)
        
        # 状态栏
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        """创建头部区域"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_label = tk.Label(header_frame, 
                              text="🚀 C盘深度清理工具",
                              font=('Microsoft YaHei UI', 20, 'bold'),
                              fg=THEME_COLORS['primary'])
        title_label.pack(side=tk.LEFT)
        
        # 磁盘信息卡片
        disk_frame = ttk.Frame(header_frame)
        disk_frame.pack(side=tk.RIGHT)
        
        self.disk_info_label = tk.Label(disk_frame,
                                        text="C盘使用情况加载中...",
                                        font=('Microsoft YaHei UI', 10),
                                        fg=THEME_COLORS['text'])
        self.disk_info_label.pack()
        
        self.disk_usage_bar = ttk.Progressbar(disk_frame, 
                                              length=200, 
                                              mode='determinate')
        self.disk_usage_bar.pack(pady=(5, 0))
        
    def create_results_area(self, parent):
        """创建结果显示区域"""
        results_frame = ttk.LabelFrame(parent, text="📊 扫描结果", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 各个类型的标签页
        self.tabs = {
            'summary': self.create_summary_tab(),
            'temp': self.create_list_tab("临时文件"),
            'update': self.create_list_tab("Windows更新"),
            'browser': self.create_list_tab("浏览器缓存"),
            'dev': self.create_list_tab("开发缓存"),
            'ai': self.create_list_tab("AI工具缓存"),
            'chat': self.create_list_tab("聊天软件"),
            'media': self.create_list_tab("媒体软件"),
            'large': self.create_list_tab("大文件"),
            'duplicate': self.create_list_tab("重复文件"),
            'logs': self.create_list_tab("系统日志"),
        }
        
        self.notebook.add(self.tabs['summary'], text="📋 总览")
        self.notebook.add(self.tabs['temp'], text="🗑️ 临时文件")
        self.notebook.add(self.tabs['update'], text="🔄 Windows更新")
        self.notebook.add(self.tabs['browser'], text="🌐 浏览器缓存")
        self.notebook.add(self.tabs['dev'], text="💻 开发缓存")
        self.notebook.add(self.tabs['ai'], text="🤖 AI工具缓存")
        self.notebook.add(self.tabs['chat'], text="💬 聊天软件")
        self.notebook.add(self.tabs['media'], text="🎵 媒体软件")
        self.notebook.add(self.tabs['large'], text="📦 大文件")
        self.notebook.add(self.tabs['duplicate'], text="📑 重复文件")
        self.notebook.add(self.tabs['logs'], text="📝 系统日志")
        
    def create_summary_tab(self):
        """创建总览标签页"""
        frame = ttk.Frame(self.notebook)
        
        # 滚动文本区域
        self.summary_text = scrolledtext.ScrolledText(frame, 
                                                      wrap=tk.WORD,
                                                      font=('Consolas', 10),
                                                      height=20)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始提示
        self.summary_text.insert(tk.END, "点击 '开始扫描' 按钮开始分析C盘...\n\n")
        self.summary_text.insert(tk.END, "扫描内容包括：\n")
        self.summary_text.insert(tk.END, "  ✓ Windows临时文件和更新缓存\n")
        self.summary_text.insert(tk.END, "  ✓ 浏览器缓存和历史记录\n")
        self.summary_text.insert(tk.END, "  ✓ 软件开发缓存 (node_modules, pip等)\n")
        self.summary_text.insert(tk.END, "  ✓ 系统日志和错误报告\n")
        self.summary_text.insert(tk.END, "\n")
        self.summary_text.insert(tk.END, "⚡ 快速模式：暂不扫描大文件和重复文件（避免太慢）\n")
        self.summary_text.insert(tk.END, "   预计扫描时间：1-3分钟\n")
        self.summary_text.config(state=tk.DISABLED)
        
        return frame
    
    def create_list_tab(self, tab_name):
        """创建列表标签页"""
        frame = ttk.Frame(self.notebook)
        
        # 创建Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        tree = ttk.Treeview(tree_frame, 
                           columns=('路径', '大小', '文件数'),
                           show='tree headings',
                           yscrollcommand=scrollbar.set)
        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)
        
        # 列标题
        tree.heading('#0', text='选择')
        tree.heading('路径', text='路径')
        tree.heading('大小', text='大小')
        tree.heading('文件数', text='文件数量')
        
        # 列宽度
        tree.column('#0', width=50)
        tree.column('路径', width=400)
        tree.column('大小', width=120)
        tree.column('文件数', width=100)
        
        # 保存tree引用
        frame.tree = tree
        
        return frame
    
    def create_action_buttons(self, parent):
        """创建操作按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始扫描按钮
        self.scan_button = ttk.Button(button_frame,
                                     text="🔍 开始扫描",
                                     style='Primary.TButton',
                                     command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 全选按钮
        self.select_all_button = ttk.Button(button_frame,
                                           text="☑️ 全选",
                                           command=self.select_all,
                                           state=tk.DISABLED)
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清理按钮
        self.clean_button = ttk.Button(button_frame,
                                      text="🧹 清理选中项",
                                      style='Success.TButton',
                                      command=self.start_clean,
                                      state=tk.DISABLED)
        self.clean_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 高级扫描按钮（大文件+重复文件）
        self.advanced_scan_button = ttk.Button(button_frame,
                                              text="🔬 高级扫描",
                                              command=self.start_advanced_scan,
                                              state=tk.DISABLED)
        self.advanced_scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新磁盘信息按钮
        self.refresh_button = ttk.Button(button_frame,
                                        text="🔄 刷新",
                                        command=self.update_disk_info)
        self.refresh_button.pack(side=tk.RIGHT)
        
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_frame,
                                    text="就绪",
                                    anchor=tk.W,
                                    font=('Microsoft YaHei UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(status_frame,
                                           length=200,
                                           mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
    def update_disk_info(self):
        """更新磁盘使用情况"""
        try:
            import psutil
            disk = psutil.disk_usage('C:\\')
            
            used_gb = disk.used / (1024**3)
            total_gb = disk.total / (1024**3)
            free_gb = disk.free / (1024**3)
            percent = disk.percent
            
            info_text = f"C盘: {used_gb:.1f}GB / {total_gb:.1f}GB 使用 ({percent}%) | 剩余: {free_gb:.1f}GB"
            self.disk_info_label.config(text=info_text)
            
            self.disk_usage_bar['value'] = percent
            
            # 根据使用率改变颜色
            if percent > 90:
                self.disk_info_label.config(fg=THEME_COLORS['danger'])
            elif percent > 75:
                self.disk_info_label.config(fg=THEME_COLORS['warning'])
            else:
                self.disk_info_label.config(fg=THEME_COLORS['success'])
                
        except Exception as e:
            self.disk_info_label.config(text=f"无法获取磁盘信息: {e}")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_scan(self):
        """开始扫描"""
        # 禁用按钮
        self.scan_button.config(state=tk.DISABLED)
        self.clean_button.config(state=tk.DISABLED)
        self.select_all_button.config(state=tk.DISABLED)
        
        # 清空之前的结果
        self.clear_results()
        
        # 显示进度
        self.progress_bar.start()
        self.update_status("正在扫描C盘...")
        
        # 在新线程中执行扫描
        scan_thread = threading.Thread(target=self.perform_scan)
        scan_thread.daemon = True
        scan_thread.start()
    
    def perform_scan(self):
        """执行扫描（在后台线程中）"""
        try:
            def progress_callback(task_name, progress):
                self.root.after(0, self.update_status, f"正在扫描: {task_name}...")
            
            print("\n" + "="*60)
            print("开始扫描C盘...")
            print("="*60)
            
            # 执行快速扫描（不包括大文件和重复文件检测，那些太慢了）
            results = self.cleaner.perform_full_scan(
                progress_callback,
                enable_large_files=False,  # 暂时关闭大文件扫描
                enable_duplicates=False    # 暂时关闭重复文件检测
            )
            
            print("\n" + "="*60)
            print("扫描完成！")
            print("="*60 + "\n")
            
            # 在主线程中更新UI
            self.root.after(0, self.display_results, results)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"\n[严重错误] 扫描失败:\n{error_detail}")
            self.root.after(0, self.show_error, f"扫描失败: {e}\n\n请查看控制台获取详细错误信息")
        finally:
            self.root.after(0, self.scan_complete)
    
    def display_results(self, results):
        """显示扫描结果"""
        self.scan_results = results
        
        # 更新总览
        self.update_summary_tab(results)
        
        # 更新各个标签页
        self.update_temp_tab(results.get('temp_files', {}))
        self.update_windows_update_tab(results.get('windows_update', {}))
        self.update_browser_tab(results.get('browser_cache', {}))
        self.update_dev_tab(results.get('dev_cache', {}))
        self.update_ai_tab(results.get('ai_cache', {}))
        self.update_chat_tab(results.get('chat_cache', {}))
        self.update_media_tab(results.get('media_cache', {}))
        self.update_large_files_tab(results.get('large_files', {}))
        self.update_duplicate_tab(results.get('duplicates', {}))
        self.update_logs_tab(results.get('system_logs', {}))
        
        # 显示结果摘要
        total_size = results.get('summary', {}).get('total_size', 0)
        messagebox.showinfo("扫描完成", 
                          f"扫描完成！\n\n可释放空间: {humanize.naturalsize(total_size)}\n\n"
                          "请在各个标签页中查看详情并选择要清理的项目。")
    
    def update_summary_tab(self, results):
        """更新总览标签页"""
        summary = results.get('summary', {})
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        self.summary_text.insert(tk.END, "=" * 60 + "\n")
        self.summary_text.insert(tk.END, "C盘深度扫描报告\n")
        self.summary_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.summary_text.insert(tk.END, f"📊 总体概况\n")
        self.summary_text.insert(tk.END, f"   可释放空间: {summary.get('total_size_readable', '0 B')}\n\n")
        
        # 临时文件
        temp = results.get('temp_files', {})
        self.summary_text.insert(tk.END, f"🗑️  临时文件: {humanize.naturalsize(temp.get('total_size', 0))} ({temp.get('file_count', 0)} 个文件)\n")
        
        # Windows更新
        update = results.get('windows_update', {})
        self.summary_text.insert(tk.END, f"🔄 Windows更新缓存: {humanize.naturalsize(update.get('total_size', 0))}\n")
        
        # 浏览器缓存
        browser = results.get('browser_cache', {})
        self.summary_text.insert(tk.END, f"🌐 浏览器缓存: {humanize.naturalsize(browser.get('total_size', 0))}\n")
        
        # 开发缓存
        dev = results.get('dev_cache', {})
        self.summary_text.insert(tk.END, f"💻 开发缓存: {humanize.naturalsize(dev.get('total_size', 0))}\n")
        
        # AI工具缓存
        ai = results.get('ai_cache', {})
        self.summary_text.insert(tk.END, f"🤖 AI工具缓存: {humanize.naturalsize(ai.get('total_size', 0))}\n")
        
        # 聊天软件缓存
        chat = results.get('chat_cache', {})
        self.summary_text.insert(tk.END, f"💬 聊天软件缓存: {humanize.naturalsize(chat.get('total_size', 0))}\n")
        
        # 媒体软件缓存
        media = results.get('media_cache', {})
        self.summary_text.insert(tk.END, f"🎵 媒体软件缓存: {humanize.naturalsize(media.get('total_size', 0))}\n")
        
        # 系统日志
        logs = results.get('system_logs', {})
        self.summary_text.insert(tk.END, f"📝 系统日志: {humanize.naturalsize(logs.get('total_size', 0))}\n\n")
        
        # 大文件分析（如果启用）
        if 'large_files' in results:
            large = results.get('large_files', {})
            self.summary_text.insert(tk.END, f"📦 大文件分析:\n")
            self.summary_text.insert(tk.END, f"   找到 {large.get('file_count', 0)} 个大于 {LARGE_FILE_THRESHOLD}MB 的文件\n")
            self.summary_text.insert(tk.END, f"   总大小: {humanize.naturalsize(large.get('total_size', 0))}\n\n")
            hidden_count = large.get('hidden_critical_count', 0)
            if hidden_count > 0:
                self.summary_text.insert(tk.END, f"   🛡️ 已自动隐藏系统关键文件: {hidden_count} 个\n\n")
        else:
            self.summary_text.insert(tk.END, f"📦 大文件分析: 未启用（节省时间）\n\n")
        
        # 重复文件（如果启用）
        if 'duplicates' in results:
            dup = results.get('duplicates', {})
            self.summary_text.insert(tk.END, f"📑 重复文件检测:\n")
            self.summary_text.insert(tk.END, f"   找到 {len(dup.get('duplicates', []))} 组重复文件\n")
            self.summary_text.insert(tk.END, f"   可节省空间: {humanize.naturalsize(dup.get('total_size', 0))}\n\n")
        else:
            self.summary_text.insert(tk.END, f"📑 重复文件检测: 未启用（节省时间）\n\n")
        
        self.summary_text.insert(tk.END, "=" * 60 + "\n")
        self.summary_text.insert(tk.END, "💡 提示: 请在各标签页中选择要清理的项目\n")
        self.summary_text.insert(tk.END, "=" * 60 + "\n")
        
        self.summary_text.config(state=tk.DISABLED)
    
    def update_temp_tab(self, data):
        """更新临时文件标签页"""
        tree = self.tabs['temp'].tree
        tree.delete(*tree.get_children())
        
        for item in data.get('paths', []):
            tree.insert('', tk.END, 
                       values=(item['path'], item['size_readable'], item.get('file_count', 'N/A')),
                       tags=('cleanable',))
    
    def update_windows_update_tab(self, data):
        """更新Windows更新标签页"""
        tree = self.tabs['update'].tree
        tree.delete(*tree.get_children())
        
        for item in data.get('paths', []):
            tree.insert('', tk.END,
                       values=(item['path'], item['size_readable'], item.get('file_count', 'N/A')),
                       tags=('cleanable',))
    
    def update_browser_tab(self, data):
        """更新浏览器缓存标签页"""
        tree = self.tabs['browser'].tree
        tree.delete(*tree.get_children())
        
        for browser_name, browser_data in data.get('browsers', {}).items():
            parent = tree.insert('', tk.END, text=browser_name,
                               values=(f"{browser_name} ({len(browser_data['paths'])} 个路径)",
                                      humanize.naturalsize(browser_data['size']),
                                      browser_data.get('file_count', 'N/A')))
            
            for path_item in browser_data['paths']:
                tree.insert(parent, tk.END,
                          values=(path_item['path'], path_item['size_readable'], ''),
                          tags=('cleanable',))
    
    def update_dev_tab(self, data):
        """更新开发缓存标签页"""
        tree = self.tabs['dev'].tree
        tree.delete(*tree.get_children())
        
        # 全局缓存
        if data.get('global_caches'):
            global_parent = tree.insert('', tk.END, text='全局缓存',
                                       values=('全局缓存路径', '', ''))
            for cache_name, cache_data in data['global_caches'].items():
                tree.insert(global_parent, tk.END,
                          values=(f"{cache_name}: {cache_data['path']}", 
                                 cache_data['size_readable'],
                                 cache_data.get('file_count', 'N/A')),
                          tags=('cleanable',))
        
        # 项目缓存文件夹
        if data.get('folders'):
            folder_parent = tree.insert('', tk.END, text='项目缓存文件夹',
                                      values=(f'{len(data["folders"])} 个文件夹', '', ''))
            for folder in data['folders']:
                tree.insert(folder_parent, tk.END,
                          values=(f"[{folder['type']}] {folder['path']}", 
                                 folder['size_readable'], ''),
                          tags=('cleanable',))
    
    def update_ai_tab(self, data):
        """更新AI工具缓存标签页"""
        tree = self.tabs['ai'].tree
        tree.delete(*tree.get_children())
        
        for tool_name, tool_data in data.get('tools', {}).items():
            tree.insert('', tk.END,
                       values=(f"{tool_name}: {tool_data['path']}", 
                              tool_data['size_readable'],
                              tool_data.get('file_count', 'N/A')),
                       tags=('cleanable',))
    
    def update_chat_tab(self, data):
        """更新聊天软件缓存标签页"""
        tree = self.tabs['chat'].tree
        tree.delete(*tree.get_children())
        
        for app_name, app_data in data.get('apps', {}).items():
            parent = tree.insert('', tk.END, text=app_name,
                               values=(f"{app_name} ({len(app_data.get('paths', []))} 个路径)",
                                      humanize.naturalsize(app_data.get('size', 0)),
                                      app_data.get('file_count', 'N/A')))
            
            for path_item in app_data.get('paths', []):
                tree.insert(parent, tk.END,
                          values=(path_item['path'], path_item['size_readable'], ''),
                          tags=('cleanable',))
    
    def update_media_tab(self, data):
        """更新媒体软件缓存标签页"""
        tree = self.tabs['media'].tree
        tree.delete(*tree.get_children())
        
        for app_name, app_data in data.get('apps', {}).items():
            tree.insert('', tk.END,
                       values=(f"{app_name}: {app_data['path']}", 
                              app_data['size_readable'],
                              app_data.get('file_count', 'N/A')),
                       tags=('cleanable',))
    
    def update_large_files_tab(self, data):
        """更新大文件标签页"""
        tree = self.tabs['large'].tree
        tree.delete(*tree.get_children())

        # 顶部提示：系统关键文件已自动隐藏
        hidden_count = data.get('hidden_critical_count', 0)
        hidden_size = data.get('hidden_critical_size', 0)
        if hidden_count > 0:
            tree.insert('', 0,
                       values=(f"🛡️ 已自动隐藏系统关键文件 {hidden_count} 个（如 pagefile.sys）",
                              humanize.naturalsize(hidden_size),
                              '已保护'))
        
        # 然后显示其他大文件，按安全级别分组
        if data.get('files'):
            # 分类文件
            dangerous_files = [f for f in data['files'] if f.get('safety_level') == 'dangerous']
            warning_files = [f for f in data['files'] if f.get('safety_level') == 'warning']
            safe_files = [f for f in data['files'] if f.get('safety_level') == 'safe']
            
            # 显示危险文件
            if dangerous_files:
                danger_parent = tree.insert('', tk.END, text='⚠️ 系统目录文件 - 谨慎处理',
                                           values=(f'{len(dangerous_files)} 个文件', '', ''))
                for file in dangerous_files:
                    tree.insert(danger_parent, tk.END,
                               values=(f"⚠️ {file['path']}", 
                                      file['size_readable'], 
                                      file['extension']),
                               tags=('dangerous',))
            
            # 显示安全文件
            if safe_files:
                safe_parent = tree.insert('', tk.END, text='✅ 可安全删除的文件',
                                         values=(f'{len(safe_files)} 个文件', '', ''))
                for file in safe_files:
                    tree.insert(safe_parent, tk.END,
                               values=(f"✅ {file['path']}", 
                                      file['size_readable'], 
                                      file['extension']),
                               tags=('safe',))
            
            # 显示需要确认的文件
            if warning_files:
                warning_parent = tree.insert('', tk.END, text='⚡ 请确认是否需要',
                                            values=(f'{len(warning_files)} 个文件', '', ''))
                for file in warning_files:
                    tree.insert(warning_parent, tk.END,
                               values=(f"⚡ {file['path']}", 
                                      file['size_readable'], 
                                      file['extension']),
                               tags=('warning',))
        
        # 配置颜色标签
        tree.tag_configure('dangerous', foreground='#FF6B00')  # 橙色
        tree.tag_configure('safe', foreground='#00AA00')      # 绿色
        tree.tag_configure('warning', foreground='#0066CC')   # 蓝色
    
    def update_duplicate_tab(self, data):
        """更新重复文件标签页"""
        tree = self.tabs['duplicate'].tree
        tree.delete(*tree.get_children())
        
        for dup_group in data.get('duplicates', []):
            parent = tree.insert('', tk.END,
                               values=(f"重复文件组 ({dup_group['count']} 个文件)",
                                      dup_group['wasted_space_readable'],
                                      dup_group['count']))
            
            for file in dup_group['files']:
                tree.insert(parent, tk.END,
                          values=(file['path'], file['size_readable'], ''),
                          tags=('cleanable',))
    
    def update_logs_tab(self, data):
        """更新系统日志标签页"""
        tree = self.tabs['logs'].tree
        tree.delete(*tree.get_children())
        
        for item in data.get('paths', []):
            tree.insert('', tk.END,
                       values=(item['path'], item['size_readable'], item.get('file_count', 'N/A')),
                       tags=('cleanable',))
    
    def clear_results(self):
        """清空结果"""
        for tab_name, tab_frame in self.tabs.items():
            if tab_name != 'summary' and hasattr(tab_frame, 'tree'):
                tab_frame.tree.delete(*tab_frame.tree.get_children())
    
    def scan_complete(self):
        """扫描完成后的处理"""
        self.progress_bar.stop()
        self.update_status("扫描完成")
        self.scan_button.config(state=tk.NORMAL)
        self.clean_button.config(state=tk.NORMAL)
        self.select_all_button.config(state=tk.NORMAL)
        self.advanced_scan_button.config(state=tk.NORMAL)  # 启用高级扫描按钮
    
    def select_all(self):
        """全选当前标签页的项目"""
        current_tab_id = self.notebook.select()
        
        for tab_name, tab_frame in self.tabs.items():
            if str(tab_frame) == current_tab_id and hasattr(tab_frame, 'tree'):
                tree = tab_frame.tree
                children = tree.get_children()
                
                if not children:
                    messagebox.showinfo("提示", "当前标签页没有可选项")
                    return
                
                selected_count = 0
                for item in children:
                    if tree.item(item, 'open'):
                        for child in tree.get_children(item):
                            tree.selection_add(child)
                            selected_count += 1
                    tree.selection_add(item)
                    selected_count += 1
                
                messagebox.showinfo("提示", f"已选中 {selected_count} 个项目")
                return
        
        messagebox.showinfo("提示", "请先选择一个标签页")
    
    def start_clean(self):
        """开始清理"""
        selected_items = []
        seen_paths = set()
        
        current_tab_id = self.notebook.select()
        
        for tab_name, tab_frame in self.tabs.items():
            if tab_name == 'summary' or not hasattr(tab_frame, 'tree'):
                continue
            
            tree = tab_frame.tree
            selection = tree.selection()
            
            for item in selection:
                values = tree.item(item, 'values')
                if values and len(values) > 0:
                    path = values[0]
                    if ':' in path or path.startswith('C:\\'):
                        normalized = path.strip().lower()
                        if normalized not in seen_paths:
                            selected_items.append(path)
                            seen_paths.add(normalized)
        
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要清理的项目")
            return
        
        # 确认清理
        response = messagebox.askyesno(
            "确认清理",
            f"确定要清理 {len(selected_items)} 个项目吗？\n\n"
            "⚠️ 此操作不可撤销！\n"
            "建议先确认列表中没有重要文件。\n\n"
            "是否继续？"
        )
        
        if response:
            # 禁用按钮
            self.scan_button.config(state=tk.DISABLED)
            self.clean_button.config(state=tk.DISABLED)
            self.select_all_button.config(state=tk.DISABLED)
            if hasattr(self, 'advanced_scan_button'):
                self.advanced_scan_button.config(state=tk.DISABLED)
            
            # 显示进度
            self.progress_bar.start()
            self.update_status("正在清理...")
            
            # 在新线程中执行清理
            clean_thread = threading.Thread(target=self.perform_clean, args=(selected_items,))
            clean_thread.daemon = True
            clean_thread.start()
    
    def perform_clean(self, selected_items):
        """执行清理（在后台线程中）"""
        try:
            print("\n" + "="*60)
            print(f"开始清理 {len(selected_items)} 个项目...")
            print("="*60)
            
            # 清理结果
            cleaned_results = self.cleaner.clean_selected_items(
                selected_items,
                progress_callback=lambda path, progress: self.root.after(
                    0, self.update_status, f"正在清理: {os.path.basename(path)}..."
                )
            )
            
            print("\n" + "="*60)
            print("清理完成！")
            print("="*60)
            
            # 在主线程中更新UI
            self.root.after(0, self.display_clean_results, cleaned_results)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"\n[严重错误] 清理失败:\n{error_detail}")
            self.root.after(0, self.show_error, f"清理失败: {e}")
        finally:
            self.root.after(0, self.clean_complete)
    
    def display_clean_results(self, results):
        """显示清理结果"""
        success_count = len(results['success'])
        failed_count = len(results['failed'])
        total_cleaned = results['total_cleaned']
        
        msg = f"清理完成！\n\n"
        msg += f"✅ 成功清理: {success_count} 个项目\n"
        msg += f"❌ 清理失败: {failed_count} 个项目\n"
        msg += f"📊 释放空间: {humanize.naturalsize(total_cleaned)}\n\n"
        msg += f"🗑️ 提示: 文件已移到回收站\n"
        msg += f"   如需彻底释放空间，请清空回收站\n\n"
        
        if failed_count > 0:
            msg += "失败的项目:\n"
            for item in results['failed'][:5]:  # 只显示前5个
                msg += f"  - {os.path.basename(item['path'])}\n"
            if failed_count > 5:
                msg += f"  ... 还有 {failed_count - 5} 个\n"
        
        messagebox.showinfo("清理完成", msg)
        
        # 刷新磁盘信息
        self.update_disk_info()
        
        # 清空结果，建议重新扫描
        response = messagebox.askyesno(
            "重新扫描",
            "是否重新扫描以更新结果？"
        )
        if response:
            self.start_scan()
    
    def clean_complete(self):
        """清理完成后的处理"""
        self.progress_bar.stop()
        self.update_status("清理完成")
        self.scan_button.config(state=tk.NORMAL)
        self.clean_button.config(state=tk.NORMAL)
        self.select_all_button.config(state=tk.NORMAL)
        if hasattr(self, 'advanced_scan_button'):
            self.advanced_scan_button.config(state=tk.NORMAL)
    
    def start_advanced_scan(self):
        """开始高级扫描（大文件+重复文件）"""
        response = messagebox.askyesno(
            "高级扫描",
            "高级扫描包括：\n\n"
            "📦 大文件分析（>100MB）\n"
            "📑 重复文件检测（MD5哈希）\n\n"
            "⚠️ 警告：此过程可能需要10-30分钟\n\n"
            "是否继续？"
        )
        
        if response:
            # 禁用按钮
            self.scan_button.config(state=tk.DISABLED)
            self.clean_button.config(state=tk.DISABLED)
            self.advanced_scan_button.config(state=tk.DISABLED)
            
            # 显示进度
            self.progress_bar.start()
            self.update_status("正在进行高级扫描...")
            
            # 在新线程中执行高级扫描
            scan_thread = threading.Thread(target=self.perform_advanced_scan)
            scan_thread.daemon = True
            scan_thread.start()
    
    def perform_advanced_scan(self):
        """执行高级扫描（在后台线程中）"""
        try:
            print("\n" + "="*60)
            print("开始高级扫描...")
            print("="*60)
            
            # 扫描大文件
            self.root.after(0, self.update_status, "正在扫描大文件...")
            large_files = self.cleaner.scan_large_files()
            
            # 扫描重复文件
            self.root.after(0, self.update_status, "正在检测重复文件...")
            duplicates = self.cleaner.scan_duplicate_files()
            
            print("\n" + "="*60)
            print("高级扫描完成！")
            print("="*60 + "\n")
            
            # 更新UI
            self.root.after(0, self.display_advanced_results, large_files, duplicates)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"\n[严重错误] 高级扫描失败:\n{error_detail}")
            self.root.after(0, self.show_error, f"高级扫描失败: {e}")
        finally:
            self.root.after(0, self.advanced_scan_complete)
    
    def display_advanced_results(self, large_files, duplicates):
        """显示高级扫描结果"""
        # 更新大文件标签页
        self.update_large_files_tab(large_files)
        
        # 更新重复文件标签页
        self.update_duplicate_tab(duplicates)
        
        # 显示结果摘要
        total_large = large_files.get('file_count', 0)
        total_dup = len(duplicates.get('duplicates', []))
        
        messagebox.showinfo(
            "高级扫描完成",
            f"高级扫描完成！\n\n"
            f"📦 大文件：{total_large} 个\n"
            f"📑 重复文件组：{total_dup} 组\n\n"
            f"请在相应标签页查看详情。"
        )
    
    def advanced_scan_complete(self):
        """高级扫描完成后的处理"""
        self.progress_bar.stop()
        self.update_status("高级扫描完成")
        self.scan_button.config(state=tk.NORMAL)
        self.clean_button.config(state=tk.NORMAL)
        self.advanced_scan_button.config(state=tk.NORMAL)
    
    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        self.progress_bar.stop()
        self.update_status("错误")
        self.scan_button.config(state=tk.NORMAL)


def main():
    """主函数"""
    root = tk.Tk()
    app = CleanerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
