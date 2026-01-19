#!/usr/bin/env python3
"""
RemUp 文件拖拽编译器 v3.1 - 修复项目根目录检测
"""

import os
import sys
import subprocess
import argparse
import shlex
from pathlib import Path

def get_project_root():
    """检测项目根目录（包含static/css的目录）"""
    possible_roots = [
        # 1. 当前工作目录
        Path.cwd(),
        # 2. 脚本文件所在目录
        Path(__file__).parent,
        # 3. 环境变量指定的目录
        Path(os.environ.get('REMUP_PROJECT_ROOT', '')),
    ]
    
    # 添加向上查找逻辑
    current = Path.cwd()
    for _ in range(3):  # 最多向上查找3级
        if (current / "static" / "css").exists():
            possible_roots.append(current)
        current = current.parent
    
    # 检查可能的根目录
    for root in possible_roots:
        if root.exists():
            css_dir = root / "static" / "css"
            if css_dir.exists():
                print(f"✅ 检测到项目根目录: {root}")
                return root
    
    # 如果都没找到，使用当前工作目录
    fallback_root = Path.cwd()
    print(f"⚠️ 未检测到标准项目结构，使用回退目录: {fallback_root}")
    return fallback_root

def get_venv_remup_path(project_root: Path):
    """获取虚拟环境中的remup命令路径"""
    venv_remup = project_root / ".venv" / "Scripts" / "remup.exe"
    
    if venv_remup.exists():
        return str(venv_remup)
    else:
        # 备用方案：使用虚拟环境中的Python执行模块
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            return [str(venv_python), "-m", "remup.main"]
        else:
            return "remup"  # 回退到系统PATH

def get_available_themes(remup_cmd, project_root: Path):
    """获取可用的主题列表"""
    try:
        if isinstance(remup_cmd, list):
            cmd = remup_cmd + ["--list-themes"]
        else:
            cmd = [remup_cmd, "--list-themes"]
        
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['REMUP_PROJECT_ROOT'] = str(project_root)  # 设置项目根目录环境变量
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env,
            cwd=project_root,  # 在项目根目录执行
            timeout=10
        )
        
        if result.returncode == 0:
            themes = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith("🎨") and not line.startswith("💡"):
                    if line.startswith("•"):
                        themes.append(line[1:].strip())
                    else:
                        themes.append(line)
            return themes
    except Exception as e:
        print(f"⚠️ 无法获取主题列表: {e}")
    
    return ["RemStyle"]  # 默认回退

def compile_remup_file(file_path, theme="RemStyle", remup_cmd=None, project_root=None):
    """编译单个 .remup 文件"""
    if remup_cmd is None:
        remup_cmd = get_venv_remup_path(project_root)
    
    try:
        # 确保文件路径是绝对路径
        abs_file_path = file_path.resolve()
        
        # 构建命令
        if isinstance(remup_cmd, list):
            cmd = remup_cmd + [str(abs_file_path), "-t", theme]
        else:
            cmd = [remup_cmd, str(abs_file_path), "-t", theme]
        
        print(f"🎨 使用主题: {theme}")
        print(f"🔧 执行命令: {' '.join([shlex.quote(str(arg)) for arg in cmd])}")
        
        # 设置环境变量，包含项目根目录
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['REMUP_PROJECT_ROOT'] = str(project_root)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env,
            cwd=project_root,  # 在项目根目录执行
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ 编译成功: {file_path.stem}.html")
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if any(keyword in line for keyword in ["📁", "🎨", "📂", "🃏", "💡"]):
                        print(f"   {line.strip()}")
            return True
        else:
            print(f"❌ 编译失败: {file_path.name}")
            if result.stderr:
                error_lines = [line for line in result.stderr.split('\n') if line.strip()]
                for error_line in error_lines[:3]:
                    print(f"   错误: {error_line}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 编译超时: {file_path.name} (超过60秒)")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def main():
    """主函数"""
    # 检测项目根目录
    project_root = get_project_root()
    
    parser = argparse.ArgumentParser(
        description='RemUp 拖拽编译器 - 支持多主题批量编译',
        add_help=False
    )
    
    parser.add_argument('paths', nargs='*', help='要编译的文件或目录路径')
    parser.add_argument('-t', '--theme', default='RemStyle', 
                       help='指定CSS主题 (默认: RemStyle)')
    parser.add_argument('-r', '--no-recursive', action='store_true',
                       help='不递归处理子目录')
    parser.add_argument('-l', '--list-themes', action='store_true',
                       help='列出可用主题')
    parser.add_argument('-h', '--help', action='store_true',
                       help='显示帮助信息')
    
    # 解析参数
    args, unknown_args = parser.parse_known_args()
    all_paths = args.paths + unknown_args
    
    # 获取remup命令路径
    remup_cmd = get_venv_remup_path(project_root)
    
    # 处理帮助和主题列表
    if args.help or (not all_paths and not args.list_themes):
        print("=" * 60)
        print("      RemUp 拖拽编译器 v3.1")
        print("=" * 60)
        print("📁 项目根目录:", project_root)
        print()
        print("用法：")
        print("  1. 拖拽 .remup 文件到此脚本上")
        print("  2. 拖拽包含 .remup 文件的文件夹")
        print("  3. 或使用命令行: python compile_remup.py [选项] 文件或文件夹...")
        print()
        print("选项：")
        print("  -t, --theme THEME     指定CSS主题 (默认: RemStyle)")
        print("  -r, --no-recursive    不递归处理子目录")
        print("  -l, --list-themes     列出可用主题")
        print("  -h, --help            显示此帮助信息")
        print()
        
        # 显示可用主题
        themes = get_available_themes(remup_cmd, project_root)
        if themes:
            print("🎨 可用主题:")
            for theme in themes:
                print(f"  • {theme}")
            print()
            print("💡 示例: python compile_remup.py -t DarkTheme 文件.remup")
        print("=" * 60)
        
        if not all_paths:
            input("按 Enter 键退出...")
        return 0
    
    if args.list_themes:
        themes = get_available_themes(remup_cmd, project_root)
        if themes:
            print("🎨 可用主题:")
            for theme in themes:
                print(f"  • {theme}")
        else:
            print("❌ 无法获取主题列表")
        return 0
    
    # 开始编译
    print("=" * 60)
    print("      RemUp 批量编译器 v3.1")
    print("=" * 60)
    print(f"📁 项目根目录: {project_root}")
    print()
    
    all_success = True
    processed_files = 0
    successful_compiles = 0
    
    for path_arg in all_paths:
        path = Path(path_arg)
        
        if not path.exists():
            print(f"❌ 路径不存在: {path}")
            all_success = False
            continue
        
        if path.is_file() and path.suffix.lower() == '.remup':
            # 单个文件编译
            processed_files += 1
            if compile_remup_file(path, args.theme, remup_cmd, project_root):
                successful_compiles += 1
            else:
                all_success = False
        
        elif path.is_dir():
            # 编译目录
            print(f"📁 扫描目录: {path}")
            pattern = "**/*.remup" if not args.no_recursive else "*.remup"
            remup_files = list(path.glob(pattern))
            
            if not remup_files:
                print("   未找到 .remup 文件")
                continue
                
            print(f"   找到 {len(remup_files)} 个 .remup 文件")
            print()
            
            for remup_file in remup_files:
                processed_files += 1
                if compile_remup_file(remup_file, args.theme, remup_cmd, project_root):
                    successful_compiles += 1
                else:
                    all_success = False
                print()
        
        else:
            print(f"❌ 忽略不支持的文件: {path}")
    
    # 输出总结报告
    print("=" * 60)
    print("编译总结:")
    print(f"  🎨 使用主题: {args.theme}")
    print(f"  📁 处理文件: {processed_files} 个")
    print(f"  ✅ 成功编译: {successful_compiles} 个")
    print(f"  ❌ 失败文件: {processed_files - successful_compiles} 个")
    
    if all_success and processed_files > 0:
        print("🎉 所有文件编译完成！")
    elif processed_files > 0:
        print("⚠️  部分文件编译失败，请检查错误信息")
    else:
        print("❌ 未找到可编译的文件")
    
    print("=" * 60)
    
    if len(all_paths) > 0:  # 如果是拖拽运行，暂停显示结果
        input("按 Enter 键退出...")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())