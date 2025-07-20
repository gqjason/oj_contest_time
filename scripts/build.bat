@echo off
REM 创建 Python 虚拟环境

call clean.bat

REM 检查是否已安装 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Python，请先安装 Python。
    exit /b 1
)

REM 在项目根目录创建虚拟环境目录 venv
python -m venv ..\venv
echo 正在创建虚拟环境
if exist ..\venv (
    echo 虚拟环境已创建在项目根目录的 venv 文件夹中。
) else (
    echo 虚拟环境创建失败。
    exit /b 1
)

call ..\venv\Scripts\activate.bat
call install.bat

echo 当前虚拟环境中已安装的库如下：
pip list

REM 修复1：使用小写 pyinstaller 命令
REM 修复2：合并 -i 和 --icon 参数，使用单一参数格式
pyinstaller -F -w  --icon=..\resources\icons\max.ico  --distpath ..\dist  --workpath ..\build  ..\src\main.py

REM 删除虚拟环境
deactivate >nul 2>&1
rmdir /s /q ..\venv
echo 虚拟环境已删除。