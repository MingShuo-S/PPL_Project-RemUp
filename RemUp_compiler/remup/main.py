#!/usr/bin/env python3
"""RemUp编译器命令行入口 - 支持.ru后缀"""

import argparse
import sys
from pathlib import Path

# 使用绝对导入替代相对导入
try:
    from remup.compiler import RemUpCompiler, compile_remup
except ImportError:
    # 开发环境下的回退方案
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from compiler import RemUpCompiler, compile_remup

def main():
    parser = argparse.ArgumentParser(
        description="RemUp编译器 - 将RemUp标记语言(.remup或.ru文件)转换为HTML"
    )
    parser.add_argument("input", help="输入的RemUp文件路径(.remup或.ru)或目录")
    parser.add_argument("-o", "--output", help="输出HTML文件路径或目录")
    parser.add_argument("-c", "--css", help="自定义CSS文件路径")
    parser.add_argument("-d", "--dir", action="store_true", 
                       help="编译整个目录下的.remup或.ru文件")
    
    args = parser.parse_args()
    
    try:
        compiler = RemUpCompiler()
        
        if args.dir:
            # 编译整个目录
            result = compiler.compile_directory(args.input, args.output, args.css)
            print(f"✅ 编译完成！生成了 {len(result)} 个文件")
            for file in result:
                print(f"   📄 {file}")
        else:
            # 编译单个文件
            result = compiler.compile_file(args.input, args.output, args.css)
            print(f"✅ 编译成功: {args.input} -> {result}")
        
    except Exception as e:
        print(f"❌ 编译失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()