@echo off
REM 清理旧文件
call clean.bat

REM 删除虚拟环境
deactivate >nul 2>&1
rmdir /s /q ..\venv

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Python，请先安装 Python。
    exit /b 1
)

REM 创建虚拟环境
python -m venv ..\venv
echo 正在创建虚拟环境...
if not exist ..\venv (
    echo 虚拟环境创建失败。
    exit /b 1
)

call ..\venv\Scripts\activate.bat
call install.bat

echo 当前虚拟环境中已安装的库如下：
pip list

REM 打包主程序
pyinstaller -F -w ^
--icon=..\resources\icons\max.ico ^
--add-data "..\configs;configs" ^
--add-data "..\resources\icons;resources/icons" ^
--distpath ..\dist ^
--workpath ..\build ^
--specpath ..\scripts ^
..\src\main.py


REM 删除虚拟环境
deactivate >nul 2>&1
rmdir /s /q ..\venv
echo 虚拟环境已删除。
