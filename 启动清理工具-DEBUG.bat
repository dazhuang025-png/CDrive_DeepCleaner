@echo off
chcp 65001 > nul
title C盘深度清理工具 - DEBUG模式

echo.
echo ========================================
echo   C盘深度清理工具 - DEBUG版本
echo   作者：克老 (Claude) @ 柏拉那工作室
echo ========================================
echo.
echo [提示] 此版本会显示详细的扫描日志
echo        方便查看扫描进度和排查问题
echo.
echo [优化] 已默认关闭大文件和重复文件扫描
echo        扫描时间：1-3分钟（原来30分钟）
echo.
pause

REM 运行程序，保持控制台窗口
python main.py

echo.
echo.
echo ========================================
echo   程序已结束
echo ========================================
echo.
pause
