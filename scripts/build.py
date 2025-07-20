import os
import subprocess
import sys

def main():
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"项目根目录: {project_root}")
    
    # 激活虚拟环境
    venv_script = os.path.join(project_root, "venv", "Scripts", "activate")
    if not os.path.exists(venv_script):
        print("错误: 虚拟环境未创建，请先运行 install.bat")
        sys.exit(1)
    
    # 设置路径
    resources = os.path.join(project_root, "resources")
    configs = os.path.join(project_root, "configs")
    src = os.path.join(project_root, "src")
    build_path = os.path.join(project_root, "build")
    dist_path = os.path.join(project_root, "dist")
    
    # 确保目录存在
    os.makedirs(resources, exist_ok=True)
    os.makedirs(configs, exist_ok=True)
    os.makedirs(build_path, exist_ok=True)
    os.makedirs(dist_path, exist_ok=True)
    
    # 构建 PyInstaller 命令
    cmd = [
        os.path.join(project_root, "venv", "Scripts", "pyinstaller.exe"),
        "--onefile",
        "--noconsole",
        "--name", "ContestTimer",
        "--workpath", build_path,
        "--distpath", dist_path,
        "--add-data", f"{resources};resources",
        "--add-data", f"{configs};configs",
        "--hidden-import", "pystray._win32",
        "--hidden-import", "plyer.platforms.win.notification",
        "--hidden-import", "PIL",
        os.path.join(src, "main.py")
    ]
    
    print("执行命令:", " ".join(cmd))
    
    # 运行命令
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 输出结果
    print("\n" + "="*50)
    print("标准输出:")
    print(result.stdout)
    print("\n" + "="*50)
    print("错误输出:")
    print(result.stderr)
    print("="*50)
    
    if result.returncode == 0:
        if os.path.exists(os.path.join(dist_path, "ContestTimer.exe")):
            print("\n打包成功! 可执行文件在 dist\ContestTimer.exe")
        else:
            print("\n打包完成但未找到可执行文件，请检查错误信息")
    else:
        print("\n打包失败，请检查错误信息")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main()