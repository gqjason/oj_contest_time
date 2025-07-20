import os
import shutil
import glob

def clean_project():
    # 删除 __pycache__ 文件夹
    pycache_count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path, ignore_errors=True)
            print(f"删除: {pycache_path}")
            pycache_count += 1
    print(f"已删除 {pycache_count} 个 __pycache__ 文件夹")
    
    # 删除编译文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"删除: {file_path}")
    
    # 删除构建目录
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
            print(f"删除: {folder} 文件夹")
    
    # 删除 .spec 文件
    for spec in ['*.spec', '*.SPEC']:
        for file in glob.glob(spec):
            os.remove(file)
            print(f"删除: {file}")
    
    print("清理完成!")

if __name__ == "__main__":
    clean_project()
    input("按 Enter 键退出...")