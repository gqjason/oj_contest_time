@echo off
REM 安装 requirements.txt 中的依赖库

REM 检查是否存在 requirements.txt
if not exist "..\requirements.txt" (
    echo 未找到 requirements.txt
    exit /b 1
)

REM 使用 python -m pip 安装依赖
python -m pip install -r ..\requirements.txt

REM 检查安装结果
if %errorlevel% neq 0 (
    echo "[WARNING] Dependency installation failed"
    exit /b %errorlevel%
) else (
    echo Dependency installation successfully
)