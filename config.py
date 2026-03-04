#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘深度清理工具 - 配置文件
作者：克老 (Claude) @ 柏拉那工作室
日期：2026-03-01
更新：小T @ 2026-03-04
"""

import os
from pathlib import Path

# ==================== 清理目标配置 ====================

# Windows临时文件路径
TEMP_PATHS = [
    os.environ.get('TEMP', 'C:\\Windows\\Temp'),
    os.environ.get('TMP', 'C:\\Windows\\Temp'),
    'C:\\Windows\\Temp',
    'C:\\Windows\\Prefetch',
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
]

# Windows更新缓存
WINDOWS_UPDATE_PATHS = [
    'C:\\Windows\\SoftwareDistribution\\Download',
    'C:\\Windows\\Logs',
    'C:\\Windows\\Temp',
]

# 浏览器缓存路径
BROWSER_CACHE_PATHS = {
    'Chrome': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\Cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\Code Cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\GPUCache'),
    ],
    'Edge': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Edge\\User Data\\Default\\Cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Edge\\User Data\\Default\\Code Cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Edge\\User Data\\Default\\GPUCache'),
    ],
    'Firefox': [
        os.path.join(os.environ.get('APPDATA', ''), 'Mozilla\\Firefox\\Profiles'),
    ],
    'Opera': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Opera Software\\Opera Stable\\Cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Opera Software\\Opera Stable\\Code Cache'),
    ],
    'Brave': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'BraveSoftware\\Brave-Browser\\User Data\\Default\\Cache'),
    ],
}

# 软件开发缓存
DEV_CACHE_FOLDERS = [
    'node_modules',
    '__pycache__',
    '.pytest_cache',
    '.cache',
    'dist',
    'build',
    '.eggs',
    '.mypy_cache',
    '.ruff_cache',
]

DEV_CACHE_PATHS = {
    'npm': os.path.join(os.environ.get('APPDATA', ''), 'npm-cache'),
    'pip': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'pip\\Cache'),
    'yarn': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Yarn\\Cache'),
    'composer': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Composer\\Cache'),
    'huggingface': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'huggingface\\cache'),
    'torch': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'torch\\hub'),
}

# AI工具缓存路径
AI_CACHE_PATHS = {
    'Ollama_Logs': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs\\ollama\\log'),
    'Cursor_Cache': os.path.join(os.environ.get('APPDATA', ''), 'Cursor\\CachedData'),
    'VSCode_Cache': os.path.join(os.environ.get('APPDATA', ''), 'Code\\CachedData'),
    'Trae_Cache': os.path.join(os.environ.get('APPDATA', ''), 'Trae CN\\CachedData'),
}

# 聊天软件缓存
CHAT_CACHE_PATHS = {
    'WeChat': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tencent\\WeChat\\XPlugin'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tencent\\WeChat\\Files\\Temp'),
    ],
    'QQ': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tencent\\QQ\\Temp'),
    ],
    'Telegram': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Telegram Desktop\tdata\user_data'),
    ],
    'Discord': [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Discord\\Cache'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Discord\\Code Cache'),
    ],
}

# 媒体软件缓存
MEDIA_CACHE_PATHS = {
    'Spotify': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Spotify\\Storage'),
    'NetEase_Music': os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Netease\\CloudMusic\\Cache'),
}

# 系统日志路径
LOG_PATHS = [
    'C:\\Windows\\Logs',
    'C:\\Windows\\System32\\LogFiles',
    'C:\\ProgramData\\Microsoft\\Windows\\WER',
]

# ==================== 大文件分析配置 ====================

LARGE_FILE_THRESHOLD = 100

SCAN_DRIVES = ['C:\\']

EXCLUDE_FOLDERS = [
    'C:\\Windows\\System32',
    'C:\\Program Files\\WindowsApps',
    'C:\\$Recycle.Bin',
    'C:\\System Volume Information',
]

# ==================== 重复文件检测配置 ====================

DUPLICATE_MIN_SIZE = 10

# ==================== 安全配置 ====================

ADMIN_REQUIRED_PATHS = [
    'C:\\Windows\\SoftwareDistribution',
    'C:\\Windows\\System32',
    'C:\\Windows\\Logs',
]

PROTECTED_EXTENSIONS = [
    '.sys', '.dll', '.exe', '.msi', '.ini', '.cfg'
]

PROTECTED_FOLDERS = [
    'C:\\Windows\\System32',
    'C:\\Program Files',
    'C:\\Program Files (x86)',
]

CRITICAL_SYSTEM_FILES = [
    'pagefile.sys',
    'hiberfil.sys',
    'swapfile.sys',
    'bootmgr',
    'ntldr',
    'boot.ini',
]

DANGEROUS_PATH_KEYWORDS = [
    'C:\\Windows\\',
    'C:\\Recovery\\',
    'C:\\$',
    '\\System32\\',
    '\\WinSxS\\',
    '\\Boot\\',
]

SAFE_LARGE_FILE_EXTENSIONS = [
    '.iso', '.zip', '.rar', '.7z',
    '.mp4', '.avi', '.mkv', '.mov',
    '.mp3', '.flac', '.wav',
    '.exe', '.msi',
    '.dmg', '.pkg',
    '.gguf', '.safetensors', '.bin',
]

# ==================== UI配置 ====================

APP_TITLE = "C盘深度清理工具 - 柏拉那工作室出品 v2.0"

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750

THEME_COLORS = {
    'primary': '#2563eb',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'bg': '#f3f4f6',
    'text': '#111827',
}
