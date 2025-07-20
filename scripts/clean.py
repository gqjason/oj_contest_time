import os
import shutil
import glob
import sys

def find_project_root(start_dir=None):
    """查找包含 .git 或 requirements.txt 的项目根目录"""
    if start_dir is None:
        start_dir = os.getcwd()
    
    current_dir = os.path.abspath(start_dir)
    
    # 查找项目根目录的标记文件
    markers = ['.git', 'requirements.txt', 'README.md', 'src']
    while True:
        # 检查当前目录是否包含标记文件
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        
        # 到达文件系统根目录
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    
    # 如果没找到，返回当前工作目录
    return os.getcwd()

def clean_project():
    # 确定项目根目录
    project_root = find_project_root(os.path.dirname(os.path.abspath(__file__)))
    print(f"项目根目录: {project_root}")
    os.chdir(project_root)  # 切换到项目根目录
    
    # 删除 __pycache__ 文件夹
    pycache_count = 0
    for root, dirs, files in os.walk(project_root):
        # 跳过虚拟环境目录
        if 'venv' in root or 'env' in root:
            continue
            
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path, ignore_errors=True)
                print(f"删除: {os.path.relpath(pycache_path, project_root)}")
                pycache_count += 1
            except Exception as e:
                print(f"删除失败: {pycache_path} - {str(e)}")
    print(f"已删除 {pycache_count} 个 __pycache__ 文件夹")
    
    # 删除编译文件
    compiled_files = []
    for root, dirs, files in os.walk(project_root):
        # 跳过虚拟环境目录
        if 'venv' in root or 'env' in root:
            continue
            
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    compiled_files.append(os.path.relpath(file_path, project_root))
                except Exception as e:
                    print(f"删除失败: {file_path} - {str(e)}")
    
    print(f"已删除 {len(compiled_files)} 个编译文件")
    for file in compiled_files:
        print(f"  - {file}")
    
    # 删除构建目录
    build_dirs = []
    for folder in ['build', 'dist']:
        folder_path = os.path.join(project_root, folder)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path, ignore_errors=True)
                build_dirs.append(folder)
                print(f"删除: {folder} 文件夹")
            except Exception as e:
                print(f"删除失败: {folder_path} - {str(e)}")
    
    # 删除 .spec 文件
    spec_files = []
    for spec in ['*.spec', '*.SPEC']:
        for file in glob.glob(os.path.join(project_root, spec)):
            try:
                os.remove(file)
                spec_files.append(os.path.basename(file))
                print(f"删除: {os.path.basename(file)}")
            except Exception as e:
                print(f"删除失败: {file} - {str(e)}")
    
    # 清理虚拟环境（可选）
    venv_dirs = []
    for venv_name in ['venv', 'env', '.venv']:
        venv_path = os.path.join(project_root, venv_name)
        if os.path.exists(venv_path):
            try:
                shutil.rmtree(venv_path, ignore_errors=True)
                venv_dirs.append(venv_name)
                print(f"删除: {venv_name} 虚拟环境")
            except Exception as e:
                print(f"删除失败: {venv_path} - {str(e)}")
    
    print("\n清理完成!")


if __name__ == "__main__":
    print("=" * 40)
    print("项目清理工具")
    print("=" * 40)
    
    # 确认操作
    confirm = input("确定要清理项目吗? 这将删除所有编译文件和构建产物 (y/n): ")
    if confirm.lower() != 'y':
        print("清理已取消")
        sys.exit(0)
    
    clean_project()
    input("\n按 Enter 键退出...")