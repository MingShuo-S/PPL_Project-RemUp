@echo off
chcp 65001 > nul
echo RemUp编译器 v1.0
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 切换到脚本目录
cd /d "%~dp0"

REM 运行编译器
python run.py %*

if errorlevel 1 (
    echo.
    echo 编译失败!
    pause
    exit /b 1
) else (
    echo.
    echo 编译成功!
)