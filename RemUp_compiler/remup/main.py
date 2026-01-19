#!/usr/bin/env python3
"""
RemUp命令行接口 v3.0 - 支持多主题系统
"""

import argparse
import sys
from pathlib import Path
from remup.compiler import Compiler, compile_remup, compile_remup_directory

def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='RemUp编译器 - 将RemUp标记语言编译为交互式HTML笔记',
        epilog='''
示例:
  remup notes.remup                    # 编译单个文件
  remup notes.remup -o output.html     # 指定输出文件
  remup notes.remup -t DarkTheme        # 使用暗色主题
  remup ./notes -d                      # 编译整个目录
  remup --list-themes                   # 列出可用主题
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 输入参数组
    input_group = parser.add_argument_group('输入选项')
    input_group.add_argument('input', nargs='?', 
                            help='输入文件或目录路径')
    input_group.add_argument('-d', '--directory', action='store_true',
                           help='编译整个目录而非单个文件')
    input_group.add_argument('-r', '--recursive', action='store_true',
                           help='递归处理子目录（与-d一起使用）')
    
    # 输出参数组
    output_group = parser.add_argument_group('输出选项')
    output_group.add_argument('-o', '--output', 
                            help='输出文件或目录路径')
    output_group.add_argument('-t', '--theme', default='RemStyle',
                            help='选择CSS主题（默认: RemStyle）')
    output_group.add_argument('--title', 
                            help='自定义页面标题')
    
    # 信息参数组
    info_group = parser.add_argument_group('信息选项')
    info_group.add_argument('--list-themes', action='store_true',
                          help='列出所有可用主题')
    info_group.add_argument('-v', '--version', action='store_true',
                          help='显示版本信息')
    
    args = parser.parse_args()
    
    # 显示版本信息
    if args.version:
        print("RemUp编译器 v3.0 - 多主题支持版")
        return 0
    
    # 列出可用主题
    if args.list_themes:
        compiler = Compiler()
        themes = compiler.list_available_themes()
        if themes:
            print("🎨 可用主题:")
            for theme in themes:
                print(f"  • {theme}")
            print(f"\n💡 使用示例: remup input.remup -t {themes[0]}")
        else:
            print("❌ 未找到任何主题文件")
            print("💡 请在 static/css/ 目录下添加CSS主题文件")
        return 0
    
    # 验证输入参数
    if not args.input:
        parser.print_help()
        return 1
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入路径不存在: {input_path}")
        return 1
    
    try:
        compiler = Compiler()
        
        # 编译目录
        if args.directory or input_path.is_dir():
            result_files = compile_remup_directory(
                input_dir=str(input_path),
                output_dir=args.output,
                theme=args.theme,
                recursive=args.recursive
            )
            
            if result_files:
                print(f"✅ 成功编译 {len(result_files)} 个文件")
                return 0
            else:
                print("❌ 没有文件被成功编译")
                return 1
        
        # 编译单个文件
        else:
            result_path = compile_remup(
                input_path=str(input_path),
                output_path=args.output,
                theme=args.theme,
                page_title=args.title
            )
            print(f"✅ 编译完成: {result_path}")
            return 0
            
    except Exception as e:
        print(f"❌ 编译错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())