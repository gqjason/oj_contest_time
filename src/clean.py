#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import sys
import re

from logger import FileLogger

file_name = "clean.py"
class CleanFile:

    class_name = "CleanFile"
    
    def __init__(self):
        self.logger = FileLogger()
        pass
    
    def main(self):
        # 设置控制台编码为UTF-8（解决中文显示问题）
        if sys.platform == 'win32':
            os.system('chcp 65001 >nul 2>&1')
        
        # 获取项目根目录（脚本所在目录的父目录）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)        
        
        # 显示警告信息
        self.logger.debug(f"[{file_name}][{self.class_name}]\n" +
                         "=" * 80 + 
                         "\n警告：此脚本将删除以下内容（基于项目根目录）：" +
                         "\n1. build、dist、__pycache__ 文件夹" +
                         "\n2. 所有 .spec 格式文件" +
                         "\n3. 虚拟环境文件夹（venv、.venv、env、.env）" + 
                         f"\n脚本所在目录：{script_dir}" + 
                         f"\n项目根目录：{root_dir}\n"
                         "=" * 80)
        
        self.logger.info(f"[{file_name}][{self.class_name}] 开始执行清理（项目根目录：{root_dir})")


        # 清理目标目录列表
        target_dirs = ["build", "dist", "__pycache__"]
        # 清理目标文件模式
        target_files = ["*.spec"]
        # 虚拟环境目录模式
        venv_dirs = ["venv", ".venv", "env", ".env"]
        
        # 执行清理操作
        self.clean_directories(target_dirs, root_dir)
        self.clean_files(target_files, root_dir)
        self.clean_virtual_envs(venv_dirs, root_dir)
        
        # 结束提示
        self.logger.info(f"[{file_name}][{self.class_name}]\n" + 
                         "=" * 80 + 
                         "\n[清理完成] 所有操作已执行完毕" + 
                         "\n注意：部分文件/目录可能因被占用或权限问题未删除" + 
                         "\n可手动检查项目根目录：{root_dir}\n"+
                         "=" * 80)
        
        # 非Windows系统下暂停
        if sys.platform != 'win32':
            input("按 Enter 键退出...")
        
    # 清理目录函数
    def clean_directories(self, directory_names, root_dir):
        for dir_name in directory_names:
            self.logger.info(f"[{file_name}][{self.class_name}] [正在清理] {dir_name} 目录...")
            removed_count = 0
            skip_count = 0
            error_count = 0
            
            for root_path, dirs, files in os.walk(root_dir, topdown=False):
                # 检查当前目录是否在项目根目录范围内
                if not root_path.startswith(root_dir):
                    skip_count += len(dirs)
                    continue
                
                for dir in dirs:
                    if dir == dir_name:
                        full_path = os.path.join(root_path, dir)
                        try:
                            # 安全验证：确保路径在项目根目录下
                            if not full_path.startswith(root_dir):
                                self.logger.critical(f"[{file_name}][{self.class_name}] [跳过]目录不在项目根目录范围内：{full_path}")
                                skip_count += 1
                                continue
                            
                            # 删除目录
                            shutil.rmtree(full_path, ignore_errors=False)
                            self.logger.info(f"[{file_name}][{self.class_name}] 删除目录：{full_path}")
                            removed_count += 1
                        except Exception as e: 
                            self.logger.error(f"[{file_name}][{self.class_name}][clean_directories] [删除失败] {full_path} - 原因：{str(e)}")
                            error_count += 1
            
            self.logger.info(f"[{file_name}][{self.class_name}] [完成] {dir_name} 目录清理 - 删除: {removed_count}, 跳过: {skip_count}, 失败: {error_count}")

    # 清理文件函数
    def clean_files(self, file_patterns, root_dir):
        for pattern in file_patterns:
            self.logger.info(f"[{file_name}][{self.class_name}] [正在清理] {pattern} 文件...")
            removed_count = 0
            skip_count = 0
            error_count = 0
            
            # 编译正则表达式模式（支持简单通配符）
            regex = re.compile(pattern.replace('.', r'\.').replace('*', '.*') + '$')
            
            for root_path, dirs, files in os.walk(root_dir):
                for file in files:
                    if regex.match(file):
                        full_path = os.path.join(root_path, file)
                        try:
                            # 安全验证
                            if not full_path.startswith(root_dir):
                                self.logger.critical(f"[{file_name}][{self.class_name}] [跳过] 文件不在项目根目录范围内：{full_path}")
                                skip_count += 1
                                continue
                            
                            # 删除文件
                            os.remove(full_path)
                            self.logger.info(f"[{file_name}][{self.class_name}] 删除文件：{full_path}")
                            removed_count += 1
                        except Exception as e:
                            self.logger.error(f"[{file_name}][{self.class_name}][clean_directories] [删除失败] {full_path} - 原因：{str(e)}")
                            error_count += 1
            
            self.logger.info(f"[{file_name}][{self.class_name}] [完成] {pattern} 文件清理 - 删除: {removed_count}, 跳过: {skip_count}, 失败: {error_count}")
        
    # 清理虚拟环境
    def clean_virtual_envs(self, venv_names, root_dir):
        self.logger.info(f"[{file_name}][{self.class_name}] [正在清理] 虚拟环境目录...")
        removed_count = 0
        skip_count = 0
        error_count = 0
        
        for venv_name in venv_names:
            for root_path, dirs, files in os.walk(root_dir, topdown=False):
                for dir in dirs:
                    if dir == venv_name:
                        full_path = os.path.join(root_path, dir)
                        try:
                            # 安全验证
                            if not full_path.startswith(root_dir):
                                self.logger.critical(f"[{file_name}][{self.class_name}] [跳过] 虚拟环境不在项目根目录范围内：{full_path}")
                                skip_count += 1
                                continue
                            
                            # 删除虚拟环境
                            shutil.rmtree(full_path, ignore_errors=False)
                            self.logger.info(f"[{file_name}][{self.class_name}] 删除虚拟环境：{full_path}")
                            removed_count += 1
                        except Exception as e:
                            self.logger.error(f"[{file_name}][{self.class_name}][clean_directories] [删除失败] {full_path} - 原因：{str(e)}")
                            error_count += 1
        
        self.logger.info(f"[{file_name}][{self.class_name}] [完成] 虚拟环境目录清理 - 删除: {removed_count}, 跳过: {skip_count}, 失败: {error_count}")
        

if __name__ == "__main__":
    pass
    cleanfile = CleanFile()
    cleanfile.main()