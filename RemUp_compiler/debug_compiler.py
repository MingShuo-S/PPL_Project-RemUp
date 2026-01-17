#!/usr/bin/env python3
"""
调试版编译器 - 直接运行，不依赖包安装
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_compile():
    """调试编译过程"""
    input_file = Path("examples/test.ru")
    output_dir = Path("output")
    
    print("🔍 调试RemUp编译器")
    print("=" * 50)
    
    # 读取源文件
    with open(input_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    print("📄 源文件内容:")
    print(source)
    print()
    
    # 解析
    from remup.parser import Parser
    parser = Parser()
    ast = parser.parse(source)
    
    print("🌳 解析后的AST:")
    print(f"归档数量: {len(ast.archives)}")
    for i, archive in enumerate(ast.archives):
        print(f"  归档 {i}: {archive.name}")
        for j, card in enumerate(archive.cards):
            print(f"    卡片 {j}: {card.theme}")
            print(f"      标签: {len(card.labels)}")
            print(f"      区域: {len(card.regions)}")
    print()
    
    # 生成HTML
    from remup.html_generator import HTMLGenerator
    generator = HTMLGenerator()
    
    output_file = output_dir / "debug_test.html"
    result = generator.generate(ast, output_file, "调试测试")
    
    print(f"✅ 生成文件: {result}")
    
    # 显示生成的内容预览
    with open(result, 'r', encoding='utf-8') as f:
        content = f.read()
        print("📄 生成内容预览:")
        print(content[:500] + "..." if len(content) > 500 else content)

if __name__ == "__main__":
    debug_compile()