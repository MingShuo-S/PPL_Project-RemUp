#!/usr/bin/env python3
"""
RemUp 文件拖拽编译器 - 跨平台版本
支持拖拽多个文件和文件夹批量编译
"""

import os
import sys
import subprocess
from pathlib import Path

def get_venv_remup_path():
    """获取虚拟环境中的remup命令路径"""
    project_dir = Path(__file__).parent
    venv_remup = project_dir / ".venv" / "Scripts" / "remup.exe"
    
    if venv_remup.exists():
        return str(venv_remup)
    else:
        # 备用方案：使用虚拟环境中的Python执行模块
        venv_python = project_dir / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            return [str(venv_python), "-m", "cli"]
        else:
            return "remup"  # 回退到系统PATH

def compile_remup_file(file_path):
    """编译单个 .remup 文件"""
    try:
        # 获取正确的remup命令路径
        remup_cmd = get_venv_remup_path()
        
        if isinstance(remup_cmd, list):
            cmd = remup_cmd + [str(file_path)]
        else:
            cmd = [remup_cmd, str(file_path)]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 设置环境变量，确保子进程使用UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',  # 指定输出编码为UTF-8
            env=env,          # 传递修改后的环境变量
            cwd=file_path.parent
        )
        
        if result.returncode == 0:
            print(f"✅ 编译成功: {file_path.stem}.html")
            if result.stdout:
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 编译失败: {file_path.name}")
            if result.stderr:
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("      RemUp 批量编译器")
    print("=" * 50)
    print()
    
    if len(sys.argv) < 2:
        print("用法：")
        print("  1. 拖拽 .remup 文件到此脚本上")
        print("  2. 拖拽包含 .remup 文件的文件夹")
        print("  3. 或使用命令行: python compile_remup.py 文件1.remup 文件2.remup ...")
        print()
        input("按 Enter 键退出...")
        return
    
    all_success = True
    processed_files = 0
    successful_compiles = 0
    
    for arg in sys.argv[1:]:
        path = Path(arg)
        
        if path.is_file() and path.suffix.lower() == '.remup':
            # 单个文件编译
            processed_files += 1
            if compile_remup_file(path):
                successful_compiles += 1
            else:
                all_success = False
        
        elif path.is_dir():
            # 编译目录中的所有 .remup 文件
            print(f"📁 扫描目录: {path}")
            remup_files = list(path.glob("**/*.remup"))
            
            if not remup_files:
                print("   未找到 .remup 文件")
                continue
                
            print(f"   找到 {len(remup_files)} 个 .remup 文件")
            print()
            
            for remup_file in remup_files:
                processed_files += 1
                if compile_remup_file(remup_file):
                    successful_compiles += 1
                else:
                    all_success = False
                print()
        
        else:
            print(f"❌ 忽略不支持的文件: {arg}")
    
    # 输出总结报告
    print("=" * 50)
    print("编译总结:")
    print(f"  处理文件: {processed_files} 个")
    print(f"  成功编译: {successful_compiles} 个")
    print(f"  失败文件: {processed_files - successful_compiles} 个")
    
    if all_success and processed_files > 0:
        print("✅ 所有文件编译完成！")
    elif processed_files > 0:
        print("⚠️  部分文件编译失败，请检查错误信息")
    else:
        print("❌ 未找到可编译的文件")
    
    print("=" * 50)
    
    if len(sys.argv) > 1:  # 如果是拖拽运行，暂停显示结果
        input("按 Enter 键退出...")

if __name__ == "__main__":
    main()