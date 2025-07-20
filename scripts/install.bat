@echo off
setlocal

echo 正在安装Python依赖...

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0.."

:: 检查 Python 是否可用
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python。请确保 Python 已安装并添加到 PATH。
    pause
    exit /b 1
)

:: 创建虚拟环境
if not exist "%PROJECT_ROOT%\venv" (
    echo 正在创建虚拟环境...
    python -m venv "%PROJECT_ROOT%\venv"
    if %errorlevel% neq 0 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call "%PROJECT_ROOT%\venv\Scripts\activate"

:: 安装依赖
echo 正在安装依赖...
pip install --upgrade pip
if exist "%PROJECT_ROOT%\requirements.txt" (
    pip install -r "%PROJECT_ROOT%\requirements.txt"
) else (
    echo 警告: requirements.txt 不存在，安装基础依赖
    pip install pyinstaller requests beautifulsoup4 pystray plyer pillow pywin32
)

:: 验证 PyInstaller 安装
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: PyInstaller 安装失败
    pip install pyinstaller
)

echo 依赖安装完成!
echo 虚拟环境位置: %PROJECT_ROOT%\venv
echo 按任意键继续...
pause >nul