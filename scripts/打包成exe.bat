@echo off
setlocal enabledelayedexpansion

echo 正在清理旧构建...
call scripts\clean.bat

echo 正在安装依赖...
call scripts\install.bat

echo 正在打包应用程序...

:: 设置资源路径
set RESOURCES=resources
set ICONS=!RESOURCES!\icons
set CONFIGS=configs

:: 创建dist目录
if not exist dist mkdir dist

:: 使用PyInstaller打包
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name "ContestTimer" ^
  --icon "!ICONS!\app.ico" ^
  --add-data "!RESOURCES!;!RESOURCES!" ^
  --add-data "!CONFIGS!;!CONFIGS!" ^
  --hidden-import "pystray._win32" ^  # pystray的特殊依赖
  --hidden-import "plyer.platforms.win.notification" ^  # plyer的特殊依赖
  --hidden-import "PIL" ^
  --distpath dist ^
  src\main.py

:: 复制额外的资源文件
xcopy /s /y "!RESOURCES!" "dist\ContestTimer\!RESOURCES!\" >nul
xcopy /s /y "!CONFIGS!" "dist\ContestTimer\!CONFIGS!\" >nul

echo 打包完成! 可执行文件在 dist\ContestTimer 目录
pause