@echo off
echo 正在安装Python依赖...

:: 创建虚拟环境
if not exist venv (
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

echo 依赖安装完成!
echo 请使用命令 "venv\Scripts\activate" 激活虚拟环境
pause