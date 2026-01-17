#!/usr/bin/env python3
"""
RemUp编译器 - 直接运行脚本
无需安装即可使用: python run.py examples/test.ru -o output
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """主函数"""
    try:
        from remup.main import main
        sys.exit(main())
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("尝试使用简化版本...")
        return run_simple_version()

def run_simple_version():
    """简化版本运行器"""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="RemUp编译器简化版")
    parser.add_argument("input", help="输入文件")
    parser.add_argument("-o", "--output", default="./output", help="输出目录")
    parser.add_argument("-t", "--title", help="页面标题")
    
    args = parser.parse_args()
    
    print("RemUp编译器简化版 v1.0")
    print("=" * 50)
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return 1
    
    # 读取文件
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成简单HTML
    title = args.title if args.title else input_path.stem
    html_content = generate_simple_html(content, title)
    
    # 输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_path.stem}.html"
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 输入文件: {input_path}")
    print(f"✅ 输出文件: {output_file}")
    print(f"✅ 页面标题: {title}")
    print("✅ 编译完成!")
    
    return 0

def generate_simple_html(content, title):
    """生成简化版HTML"""
    from datetime import datetime
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - RemUp</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .content {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>RemUp编译器生成 - {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    </div>
    <div class="content">
        <pre>{content}</pre>
    </div>
</body>
</html>"""

if __name__ == "__main__":
    sys.exit(main())