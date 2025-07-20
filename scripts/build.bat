@echo off
setlocal enabledelayedexpansion

echo Cleaning up old builds...
call clean.bat

echo Installing dependencies...
call install.bat

echo Packaging the application...

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0.."
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

:: 激活虚拟环境
call "%PROJECT_ROOT%\venv\Scripts\activate"

:: 设置资源路径
set "RESOURCES=%PROJECT_ROOT%\resources"
set "ICONS=%RESOURCES%\icons"
set "CONFIGS=%PROJECT_ROOT%\configs"
set "SRC=%PROJECT_ROOT%\src"

:: 设置构建输出目录
set "BUILD_PATH=%PROJECT_ROOT%\build"
set "DIST_PATH=%PROJECT_ROOT%\dist"

:: 创建必要的目录
if not exist "%BUILD_PATH%" mkdir "%BUILD_PATH%"
if not exist "%DIST_PATH%" mkdir "%DIST_PATH%"
if not exist "%RESOURCES%" mkdir "%RESOURCES%"
if not exist "%ICONS%" mkdir "%ICONS%"
if not exist "%CONFIGS%" mkdir "%CONFIGS%"
if not exist "%HOOKS%" mkdir "%HOOKS%"

:: 创建临时图标文件（如果不存在）
if not exist "%ICONS%\app.ico" (
    echo 创建临时图标文件...
    copy NUL "%ICONS%\app.ico" >nul
)

:: 使用PyInstaller打包
echo 正在运行 PyInstaller...
pyinstaller --onefile --noconsole --name "ContestTimer" ^
  --workpath "%BUILD_PATH%" ^
  --distpath "%DIST_PATH%" ^
  --add-data "%RESOURCES%;resources" ^
  --add-data "%CONFIGS%;configs" ^
  --additional-hooks-dir "%HOOKS%" ^
  --hidden-import "pystray._win32" ^
  --hidden-import "plyer.platforms.win.notification" ^
  --hidden-import "PIL" ^
  --hidden-import "bs4" ^
  --hidden-import "soupsieve" ^
  "%SRC%\main.py"

:: 检查打包结果
if exist "%DIST_PATH%\ContestTimer.exe" (
    echo 打包成功! 可执行文件在 %DIST_PATH%\ContestTimer.exe
) else (
    echo 打包失败，请检查错误信息
)

echo 按任意键退出...
pause >nul