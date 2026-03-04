@echo off
chcp 65001 > nul
title C盘深度清理工具 - 柏拉那工作室

echo.
echo ========================================
echo   C盘深度清理工具
echo   作者：克老 (Claude) @ 柏拉那工作室
echo ========================================
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python环境！
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [✓] Python环境检测成功
echo.

REM 检查依赖是否安装
echo 正在检查依赖库...
python -c "import psutil, humanize" > nul 2>&1
if errorlevel 1 (
    echo [!] 缺少必要的依赖库
    echo.
    echo 正在自动安装依赖...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [错误] 依赖安装失败！
        echo 请手动运行: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [✓] 依赖安装完成
)

echo [✓] 所有依赖检查完成
echo.
echo 正在启动C盘清理工具...
echo.

REM 以管理员权限运行Python脚本
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行失败！
    echo.
    pause
    exit /b 1
)

echo.
echo 程序已退出
pause
