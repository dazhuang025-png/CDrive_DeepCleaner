#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘深度清理工具 - 核心清理功能模块
作者：克老 (Claude) @ 柏拉那工作室
日期：2026-03-01
"""

import os
import shutil
import hashlib
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple
import psutil
import humanize
import send2trash
from config import *


def is_critical_system_file(file_path: str) -> bool:
    """检查是否为系统关键文件"""
    file_name = os.path.basename(file_path).lower()
    return file_name in [f.lower() for f in CRITICAL_SYSTEM_FILES]


def is_dangerous_path(file_path: str) -> bool:
    """检查是否为危险路径"""
    file_path_upper = file_path.upper()
    return any(keyword.upper() in file_path_upper for keyword in DANGEROUS_PATH_KEYWORDS)


def get_file_safety_level(file_path: str, file_size: int = 0) -> dict:
    """
    获取文件安全等级
    返回: {
        'level': 'critical'/'dangerous'/'warning'/'safe',
        'reason': '原因说明',
        'can_delete': True/False
    }
    """
    # 检查系统关键文件
    if is_critical_system_file(file_path):
        return {
            'level': 'critical',
            'reason': '系统关键文件，删除后系统将无法启动！',
            'can_delete': False
        }
    
    # 检查危险路径
    if is_dangerous_path(file_path):
        return {
            'level': 'dangerous',
            'reason': '系统目录文件，删除可能导致系统故障',
            'can_delete': False
        }
    
    # 检查文件扩展名
    ext = os.path.splitext(file_path)[1].lower()
    if ext in SAFE_LARGE_FILE_EXTENSIONS:
        return {
            'level': 'safe',
            'reason': '可安全删除的文件类型',
            'can_delete': True
        }
    
    # 默认警告级别
    return {
        'level': 'warning',
        'reason': '请确认是否需要此文件',
        'can_delete': True
    }


def extract_windows_path(raw_text: str) -> str:
    """从带前缀文案/图标的文本中提取真实Windows路径"""
    if not raw_text:
        return ""

    text = raw_text.strip()
    # 优先匹配标准盘符路径，例如 C:\Users\...
    match = re.search(r"[A-Za-z]:\\[^\r\n]*", text)
    if match:
        return match.group(0).strip()

    # 兼容历史格式，例如 "npm: C:\..." 或 "[node_modules] C:\..."
    if ': ' in text:
        return text.split(': ', 1)[1].strip()
    if '] ' in text:
        return text.split('] ', 1)[1].strip()

    return text


class CleanerCore:
    """C盘清理核心功能类"""
    
    def __init__(self):
        self.scan_results = {}
        self.total_space_found = 0
        self.content_only_cleanup_roots = self._build_content_only_roots()

    def _build_content_only_roots(self) -> List[str]:
        """构建“仅清空内容、不删除目录本身”的路径集合"""
        roots = []
        roots.extend(TEMP_PATHS)
        roots.extend(WINDOWS_UPDATE_PATHS)
        roots.extend(LOG_PATHS)
        roots.extend(DEV_CACHE_PATHS.values())
        for browser_paths in BROWSER_CACHE_PATHS.values():
            roots.extend(browser_paths)

        normalized = []
        for path in roots:
            if not path:
                continue
            normalized.append(os.path.normcase(os.path.normpath(path)))

        return list(set(normalized))

    def _should_clean_contents_only(self, folder_path: str) -> bool:
        """判断目录是否应执行“清空内容”而不是删除目录"""
        normalized = os.path.normcase(os.path.normpath(folder_path))
        return normalized in self.content_only_cleanup_roots

    def _remove_path(self, target_path: str) -> int:
        """删除文件/目录并返回释放字节数（移到回收站）"""
        if os.path.isdir(target_path):
            size_before = self.get_folder_size(target_path)
            send2trash.send2trash(target_path)
            return size_before

        size_before = os.path.getsize(target_path)
        send2trash.send2trash(target_path)
        return size_before

    def _clean_folder_contents(self, folder_path: str) -> Tuple[int, List[Dict]]:
        """仅清空目录内容，保留目录本身"""
        cleaned_size = 0
        failed_items = []

        try:
            children = os.listdir(folder_path)
        except Exception as e:
            return 0, [{'path': folder_path, 'error': f'无法访问目录内容: {e}'}]

        for name in children:
            child_path = os.path.join(folder_path, name)
            try:
                cleaned_size += self._remove_path(child_path)
            except Exception as e:
                failed_items.append({'path': child_path, 'error': str(e)})

        return cleaned_size, failed_items
        
    def get_folder_size(self, folder_path: str) -> int:
        """获取文件夹大小（字节）"""
        size, _ = self.get_folder_size_info(folder_path)
        return size
    
    def get_folder_size_info(self, folder_path: str) -> Tuple[int, int]:
        """获取文件夹大小和文件数量（字节, 文件数）- 一次遍历完成"""
        total_size = 0
        file_count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size, file_count
    
    def scan_temp_files(self) -> Dict:
        """扫描临时文件"""
        results = {
            'paths': [],
            'total_size': 0,
            'file_count': 0
        }
        
        for temp_path in TEMP_PATHS:
            if os.path.exists(temp_path):
                try:
                    # 优化：一次遍历同时获取大小和文件数
                    size, file_count = self.get_folder_size_info(temp_path)
                    results['paths'].append({
                        'path': temp_path,
                        'size': size,
                        'size_readable': humanize.naturalsize(size),
                        'file_count': file_count
                    })
                    results['total_size'] += size
                    results['file_count'] += file_count
                except Exception as e:
                    print(f"扫描临时文件夹失败 {temp_path}: {e}")
        
        return results
    
    def scan_windows_update_cache(self) -> Dict:
        """扫描Windows更新缓存"""
        results = {
            'paths': [],
            'total_size': 0,
            'file_count': 0
        }
        
        for update_path in WINDOWS_UPDATE_PATHS:
            if os.path.exists(update_path):
                try:
                    # 优化：一次遍历同时获取大小和文件数
                    size, file_count = self.get_folder_size_info(update_path)
                    if size > 0:
                        results['paths'].append({
                            'path': update_path,
                            'size': size,
                            'size_readable': humanize.naturalsize(size),
                            'file_count': file_count
                        })
                        results['total_size'] += size
                        results['file_count'] += file_count
                except Exception as e:
                    print(f"扫描Windows更新缓存失败 {update_path}: {e}")
        
        return results
    
    def scan_browser_cache(self) -> Dict:
        """扫描浏览器缓存"""
        results = {
            'browsers': {},
            'total_size': 0,
            'file_count': 0
        }
        
        for browser_name, cache_paths in BROWSER_CACHE_PATHS.items():
            browser_data = {
                'paths': [],
                'size': 0,
                'file_count': 0
            }
            
            for cache_path in cache_paths:
                if os.path.exists(cache_path):
                    try:
                        size = self.get_folder_size(cache_path)
                        file_count = sum([len(files) for _, _, files in os.walk(cache_path)])
                        if size > 0:
                            browser_data['paths'].append({
                                'path': cache_path,
                                'size': size,
                                'size_readable': humanize.naturalsize(size)
                            })
                            browser_data['size'] += size
                            browser_data['file_count'] += file_count
                    except Exception as e:
                        print(f"扫描{browser_name}缓存失败 {cache_path}: {e}")
            
            if browser_data['size'] > 0:
                results['browsers'][browser_name] = browser_data
                results['total_size'] += browser_data['size']
                results['file_count'] += browser_data['file_count']
        
        return results
    
    def scan_dev_cache(self) -> Dict:
        """扫描软件开发缓存"""
        results = {
            'folders': [],
            'global_caches': {},
            'total_size': 0,
            'file_count': 0
        }
        
        # 扫描全局缓存
        for cache_name, cache_path in DEV_CACHE_PATHS.items():
            if os.path.exists(cache_path):
                try:
                    size = self.get_folder_size(cache_path)
                    file_count = sum([len(files) for _, _, files in os.walk(cache_path)])
                    if size > 0:
                        results['global_caches'][cache_name] = {
                            'path': cache_path,
                            'size': size,
                            'size_readable': humanize.naturalsize(size),
                            'file_count': file_count
                        }
                        results['total_size'] += size
                        results['file_count'] += file_count
                except Exception as e:
                    print(f"扫描{cache_name}缓存失败: {e}")
        
        # 扫描项目中的node_modules, __pycache__等（限制扫描深度）
        print("[提示] 开发缓存扫描可能需要1-3分钟，请耐心等待...")
        scanned_count = 0
        max_folders = 50  # 最多只扫描50个开发缓存文件夹，避免太慢
        
        for drive in SCAN_DRIVES:
            if scanned_count >= max_folders:
                break
            for folder_name in DEV_CACHE_FOLDERS:
                if scanned_count >= max_folders:
                    break
                try:
                    # 只扫描常见的项目目录，不扫描整个C盘
                    common_project_dirs = [
                        os.path.join(drive, 'Users'),
                        os.path.join(drive, 'Projects'),
                        os.path.join(drive, 'workspace'),
                    ]
                    
                    for project_dir in common_project_dirs:
                        if not os.path.exists(project_dir):
                            continue
                        
                        for root, dirs, files in os.walk(project_dir):
                            # 跳过受保护的文件夹
                            if any(root.startswith(protected) for protected in PROTECTED_FOLDERS):
                                dirs.clear()
                                continue
                            
                            # 限制扫描深度（最多3层）
                            depth = root[len(project_dir):].count(os.sep)
                            if depth > 3:
                                dirs.clear()
                                continue
                            
                            if folder_name in dirs:
                                folder_path = os.path.join(root, folder_name)
                                size = self.get_folder_size(folder_path)
                                if size > 50 * 1024 * 1024:  # 大于50MB才记录
                                    results['folders'].append({
                                        'path': folder_path,
                                        'size': size,
                                        'size_readable': humanize.naturalsize(size),
                                        'type': folder_name
                                    })
                                    results['total_size'] += size
                                    scanned_count += 1
                                    print(f"[发现] {folder_name}: {humanize.naturalsize(size)} - {folder_path}")
                                    
                                    if scanned_count >= max_folders:
                                        break
                                
                                # 找到后不再深入这个目录
                                dirs.remove(folder_name)
                except Exception as e:
                    print(f"扫描开发缓存文件夹失败: {e}")
                    continue
        
        return results
    
    def scan_large_files(self, threshold_mb: int = LARGE_FILE_THRESHOLD) -> Dict:
        """扫描大文件（隐藏系统关键文件，不纳入可清理结果）"""
        results = {
            'files': [],
            'hidden_critical_count': 0,
            'hidden_critical_size': 0,
            'total_size': 0,
            'file_count': 0
        }
        
        threshold_bytes = threshold_mb * 1024 * 1024
        
        for drive in SCAN_DRIVES:
            try:
                for root, dirs, files in os.walk(drive):
                    # 跳过受保护和排除的文件夹
                    if any(root.startswith(excluded) for excluded in EXCLUDE_FOLDERS + PROTECTED_FOLDERS):
                        continue
                    
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        try:
                            if os.path.exists(file_path):
                                size = os.path.getsize(file_path)
                                if size > threshold_bytes:
                                    ext = os.path.splitext(filename)[1].lower()
                                    
                                    # 获取安全等级
                                    safety = get_file_safety_level(file_path, size)
                                    
                                    file_info = {
                                        'path': file_path,
                                        'name': filename,
                                        'size': size,
                                        'size_readable': humanize.naturalsize(size),
                                        'extension': ext,
                                        'safety_level': safety['level'],
                                        'safety_reason': safety['reason'],
                                        'can_delete': safety['can_delete']
                                    }
                                    
                                    # 系统关键文件直接隐藏，不在结果中展示也不纳入可释放空间
                                    if safety['level'] == 'critical':
                                        results['hidden_critical_count'] += 1
                                        results['hidden_critical_size'] += size
                                        print(f"🚫 [隐藏] {humanize.naturalsize(size)} - {file_path} ({safety['reason']})")
                                        continue

                                    results['files'].append(file_info)
                                    if safety['level'] == 'dangerous':
                                        print(f"⚠️  [警告] {humanize.naturalsize(size)} - {file_path}")

                                    results['total_size'] += size
                                    results['file_count'] += 1
                        except (OSError, PermissionError):
                            continue
            except Exception as e:
                print(f"扫描大文件失败: {e}")
        
        # 按大小排序
        results['files'] = sorted(results['files'], key=lambda x: x['size'], reverse=True)
        # 只保留前100个最大的文件
        results['files'] = results['files'][:100]
        
        return results
    
    def scan_duplicate_files(self) -> Dict:
        """扫描重复文件（基于MD5哈希）"""
        results = {
            'duplicates': [],
            'total_size': 0,
            'file_count': 0
        }
        
        file_hashes = defaultdict(list)
        min_size = DUPLICATE_MIN_SIZE * 1024 * 1024
        
        for drive in SCAN_DRIVES:
            try:
                for root, dirs, files in os.walk(drive):
                    # 跳过受保护和排除的文件夹
                    if any(root.startswith(excluded) for excluded in EXCLUDE_FOLDERS + PROTECTED_FOLDERS):
                        continue
                    
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        try:
                            if os.path.exists(file_path):
                                size = os.path.getsize(file_path)
                                if size > min_size:
                                    # 计算文件MD5
                                    file_hash = self._get_file_hash(file_path)
                                    if file_hash:
                                        file_hashes[file_hash].append({
                                            'path': file_path,
                                            'size': size,
                                            'size_readable': humanize.naturalsize(size)
                                        })
                        except (OSError, PermissionError):
                            continue
            except Exception as e:
                print(f"扫描重复文件失败: {e}")
        
        # 找出重复的文件
        for file_hash, file_list in file_hashes.items():
            if len(file_list) > 1:
                duplicate_size = file_list[0]['size'] * (len(file_list) - 1)
                results['duplicates'].append({
                    'files': file_list,
                    'count': len(file_list),
                    'wasted_space': duplicate_size,
                    'wasted_space_readable': humanize.naturalsize(duplicate_size)
                })
                results['total_size'] += duplicate_size
                results['file_count'] += len(file_list) - 1
        
        # 按浪费空间排序
        results['duplicates'] = sorted(results['duplicates'], key=lambda x: x['wasted_space'], reverse=True)
        
        return results
    
    def scan_system_logs(self) -> Dict:
        """扫描系统日志"""
        results = {
            'paths': [],
            'total_size': 0,
            'file_count': 0
        }
        
        for log_path in LOG_PATHS:
            if os.path.exists(log_path):
                try:
                    size, file_count = self.get_folder_size_info(log_path)
                    if size > 0:
                        results['paths'].append({
                            'path': log_path,
                            'size': size,
                            'size_readable': humanize.naturalsize(size),
                            'file_count': file_count
                        })
                        results['total_size'] += size
                        results['file_count'] += file_count
                except Exception as e:
                    print(f"扫描系统日志失败 {log_path}: {e}")
        
        return results
    
    def scan_ai_cache(self) -> Dict:
        """扫描AI工具缓存"""
        results = {
            'tools': {},
            'total_size': 0,
            'file_count': 0
        }
        
        for tool_name, cache_path in AI_CACHE_PATHS.items():
            if cache_path and os.path.exists(cache_path):
                try:
                    size, file_count = self.get_folder_size_info(cache_path)
                    if size > 0:
                        results['tools'][tool_name] = {
                            'path': cache_path,
                            'size': size,
                            'size_readable': humanize.naturalsize(size),
                            'file_count': file_count
                        }
                        results['total_size'] += size
                        results['file_count'] += file_count
                        print(f"[发现] {tool_name}: {humanize.naturalsize(size)} - {cache_path}")
                except Exception as e:
                    print(f"扫描{tool_name}缓存失败: {e}")
        
        return results
    
    def scan_chat_cache(self) -> Dict:
        """扫描聊天软件缓存"""
        results = {
            'apps': {},
            'total_size': 0,
            'file_count': 0
        }
        
        for app_name, cache_paths in CHAT_CACHE_PATHS.items():
            app_data = {
                'paths': [],
                'size': 0,
                'file_count': 0
            }
            
            for cache_path in cache_paths:
                if cache_path and os.path.exists(cache_path):
                    try:
                        size, file_count = self.get_folder_size_info(cache_path)
                        if size > 0:
                            app_data['paths'].append({
                                'path': cache_path,
                                'size': size,
                                'size_readable': humanize.naturalsize(size)
                            })
                            app_data['size'] += size
                            app_data['file_count'] += file_count
                    except Exception as e:
                        print(f"扫描{app_name}缓存失败 {cache_path}: {e}")
            
            if app_data['size'] > 0:
                results['apps'][app_name] = app_data
                results['total_size'] += app_data['size']
                results['file_count'] += app_data['file_count']
        
        return results
    
    def scan_media_cache(self) -> Dict:
        """扫描媒体软件缓存"""
        results = {
            'apps': {},
            'total_size': 0,
            'file_count': 0
        }
        
        for app_name, cache_path in MEDIA_CACHE_PATHS.items():
            if cache_path and os.path.exists(cache_path):
                try:
                    size, file_count = self.get_folder_size_info(cache_path)
                    if size > 0:
                        results['apps'][app_name] = {
                            'path': cache_path,
                            'size': size,
                            'size_readable': humanize.naturalsize(size),
                            'file_count': file_count
                        }
                        results['total_size'] += size
                        results['file_count'] += file_count
                        print(f"[发现] {app_name}: {humanize.naturalsize(size)} - {cache_path}")
                except Exception as e:
                    print(f"扫描{app_name}缓存失败: {e}")
        
        return results
    
    def _get_file_hash(self, file_path: str, block_size: int = 65536) -> str:
        """计算文件MD5哈希值"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                buf = f.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(block_size)
            return hasher.hexdigest()
        except:
            return None
    
    def perform_full_scan(self, progress_callback=None, enable_large_files=False, enable_duplicates=False) -> Dict:
        """执行完整扫描
        
        Args:
            progress_callback: 进度回调函数
            enable_large_files: 是否启用大文件扫描（默认关闭，因为很慢）
            enable_duplicates: 是否启用重复文件检测（默认关闭，因为很慢）
        """
        all_results = {}
        
        # 基础扫描任务（快速）
        tasks = [
            ('temp_files', '临时文件', self.scan_temp_files),
            ('windows_update', 'Windows更新缓存', self.scan_windows_update_cache),
            ('browser_cache', '浏览器缓存', self.scan_browser_cache),
            ('dev_cache', '开发缓存', self.scan_dev_cache),
            ('ai_cache', 'AI工具缓存', self.scan_ai_cache),
            ('chat_cache', '聊天软件缓存', self.scan_chat_cache),
            ('media_cache', '媒体软件缓存', self.scan_media_cache),
            ('system_logs', '系统日志', self.scan_system_logs),
        ]
        
        # 可选的耗时任务
        if enable_large_files:
            tasks.append(('large_files', '大文件', self.scan_large_files))
        if enable_duplicates:
            tasks.append(('duplicates', '重复文件', self.scan_duplicate_files))
        
        for index, (key, name, func) in enumerate(tasks):
            if progress_callback:
                progress_callback(name, index / len(tasks))
            
            try:
                print(f"[扫描] 开始扫描: {name}")
                all_results[key] = func()
                print(f"[扫描] {name} 完成")
            except Exception as e:
                error_msg = f"扫描{name}时出错: {e}"
                print(f"[错误] {error_msg}")
                import traceback
                traceback.print_exc()
                all_results[key] = {'error': str(e), 'total_size': 0, 'file_count': 0}
        
        # 计算总大小
        total_size = sum([
            all_results.get('temp_files', {}).get('total_size', 0),
            all_results.get('windows_update', {}).get('total_size', 0),
            all_results.get('browser_cache', {}).get('total_size', 0),
            all_results.get('dev_cache', {}).get('total_size', 0),
            all_results.get('ai_cache', {}).get('total_size', 0),
            all_results.get('chat_cache', {}).get('total_size', 0),
            all_results.get('media_cache', {}).get('total_size', 0),
            all_results.get('system_logs', {}).get('total_size', 0),
        ])
        
        all_results['summary'] = {
            'total_size': total_size,
            'total_size_readable': humanize.naturalsize(total_size)
        }
        
        self.scan_results = all_results
        self.total_space_found = total_size
        
        return all_results
    
    def clean_selected_items(self, selected_items: List[str], progress_callback=None) -> Dict:
        """清理选中的项目"""
        cleaned_results = {
            'success': [],
            'failed': [],
            'total_cleaned': 0
        }
        
        print(f"\n开始清理 {len(selected_items)} 个项目...")
        
        for index, item_path in enumerate(selected_items):
            if progress_callback:
                progress_callback(item_path, index / len(selected_items))
            
            try:
                # 提取真实路径（兼容前缀图标/分组文案）
                real_path = extract_windows_path(item_path)
                
                if not os.path.exists(real_path):
                    print(f"[跳过] 路径不存在: {real_path}")
                    continue
                
                # 安全检查：系统关键文件
                if is_critical_system_file(real_path):
                    print(f"🚫 [禁止] 系统关键文件: {real_path}")
                    cleaned_results['failed'].append({
                        'path': real_path,
                        'error': '⚠️ 系统关键文件，删除后系统将崩溃！'
                    })
                    continue
                
                # 安全检查：危险路径
                if is_dangerous_path(real_path):
                    print(f"⚠️  [警告] 危险路径: {real_path}")
                    cleaned_results['failed'].append({
                        'path': real_path,
                        'error': '系统目录文件，为安全起见拒绝删除'
                    })
                    continue
                
                # 安全检查：不删除受保护的文件夹
                if any(real_path.startswith(protected) for protected in PROTECTED_FOLDERS):
                    print(f"[拒绝] 受保护的文件夹: {real_path}")
                    cleaned_results['failed'].append({
                        'path': real_path,
                        'error': '受保护的系统文件夹，拒绝删除'
                    })
                    continue
                
                # 安全检查：不删除受保护扩展名的文件
                if os.path.isfile(real_path):
                    ext = os.path.splitext(real_path)[1].lower()
                    if ext in PROTECTED_EXTENSIONS:
                        print(f"[拒绝] 受保护的文件类型: {real_path}")
                        cleaned_results['failed'].append({
                            'path': real_path,
                            'error': f'受保护的文件类型 ({ext})，拒绝删除'
                        })
                        continue
                
                if os.path.isdir(real_path) and self._should_clean_contents_only(real_path):
                    print(f"[清空目录内容] {real_path}")
                    cleaned_size, failed_items = self._clean_folder_contents(real_path)

                    if cleaned_size > 0:
                        cleaned_results['success'].append({
                            'path': real_path,
                            'size': cleaned_size,
                            'size_readable': humanize.naturalsize(cleaned_size)
                        })
                        cleaned_results['total_cleaned'] += cleaned_size
                        print(f"[成功] 已清空部分内容: {real_path} ({humanize.naturalsize(cleaned_size)})")

                    if failed_items:
                        cleaned_results['failed'].append({
                            'path': real_path,
                            'error': f'部分文件被占用/无权限，未能删除 {len(failed_items)} 项'
                        })

                    if cleaned_size == 0 and not failed_items:
                        print(f"[跳过] 目录为空: {real_path}")
                    continue

                size_before = self._remove_path(real_path)
                print(f"[删除] {humanize.naturalsize(size_before)} - {real_path}")

                cleaned_results['success'].append({
                    'path': real_path,
                    'size': size_before,
                    'size_readable': humanize.naturalsize(size_before)
                })
                cleaned_results['total_cleaned'] += size_before
                print(f"[成功] 已删除: {real_path}")
                
            except Exception as e:
                print(f"[失败] {real_path}: {e}")
                cleaned_results['failed'].append({
                    'path': item_path,
                    'error': str(e)
                })
        
        print(f"\n清理完成！成功: {len(cleaned_results['success'])}, 失败: {len(cleaned_results['failed'])}")
        print(f"总共释放: {humanize.naturalsize(cleaned_results['total_cleaned'])}\n")
        
        return cleaned_results
