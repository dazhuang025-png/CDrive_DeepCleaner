#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘深度清理工具 - 主程序入口
作者：克老 (Claude) @ 柏拉那工作室
日期：2026-03-01
"""

import sys
import os
import ctypes
import tkinter as tk
from tkinter import messagebox


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """请求管理员权限重新运行"""
    if sys.platform == 'win32':
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )


def main():
    """主函数"""
    print("=" * 60)
    print("C盘深度清理工具")
    print("作者：克老 (Claude) @ 柏拉那工作室")
    print("=" * 60)
    print()
    
    # 检查管理员权限
    if not is_admin():
        print("⚠️  警告: 未以管理员权限运行")
        print("某些清理功能可能无法正常工作")
        print()
        root = tk.Tk()
        root.withdraw()
        response = messagebox.askyesno(
            "需要管理员权限",
            "当前未以管理员权限运行。\n\n"
            "这会导致 Temp / Windows 更新缓存等目录清理失败。\n\n"
            "是否立即以管理员权限重启程序？"
        )
        root.destroy()

        if response:
            print("正在请求管理员权限...")
            run_as_admin()
            return
        else:
            print("继续以普通权限运行...")
    else:
        print("✓ 已获得管理员权限")
    
    print()
    print("正在启动GUI界面...")
    print()
    
    # 启动GUI
    try:
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ 错误: 缺少必要的依赖库")
        print(f"错误信息: {e}")
        print()
        print("请运行以下命令安装依赖:")
        print("  pip install -r requirements.txt")
        input("\n按回车键退出...")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()
