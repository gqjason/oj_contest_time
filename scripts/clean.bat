@echo off
setlocal

echo 正在清理Python编译文件和构建产物...

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0.."

:: 清理Python编译文件
del /s /q "%PROJECT_ROOT%\*.pyc" 2>nul
del /s /q "%PROJECT_ROOT%\*.pyo" 2>nul
del /s /q "%PROJECT_ROOT%\*.pyd" 2>nul

:: 清理构建目录
if exist "%PROJECT_ROOT%\build" rmdir /s /q "%PROJECT_ROOT%\build"
if exist "%PROJECT_ROOT%\dist" rmdir /s /q "%PROJECT_ROOT%\dist"
del /q "%PROJECT_ROOT%\*.spec" 2>nul

echo 清理完成!