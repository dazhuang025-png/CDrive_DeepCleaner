@echo off
chcp 65001 >nul
echo ============================================================
echo C盘深度清理工具 - 打包脚本
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] 清理旧的打包文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo [2/3] 开始打包...
pyinstaller --onefile --windowed --name "C盘深度清理工具" --add-data "config.py;." --hidden-import "humanize" --hidden-import "psutil" --hidden-import "send2trash" main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo [3/3] 打包完成！
echo.
echo 生成的文件位于: dist\C盘深度清理工具.exe
echo.
pause
