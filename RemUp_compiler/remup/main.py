#!/usr/bin/env python3
"""
RemUp编译器命令行入口 - 兼容新版编译器
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional

try:
    from .compiler import RemUpCompiler, CompileConfig
    from .__init__ import __version__
except ImportError:
    # 回退到直接导入
    from compiler import RemUpCompiler, CompileConfig
    __version__ = "1.0.0"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description=f"RemUp编译器 v{__version__} - 将.ru文件编译为HTML学习笔记",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 编译单个文件
  remup example.ru
  remup example.ru -o output -t "我的学习笔记"
  
  # 编译整个目录
  remup notes/ -o docs --title-prefix "知识库"
  
  # 使用配置文件
  remup --config config.json
  
  # 批量编译多个输入
  remup file1.ru file2.ru notes/ -o website --batch
  
高级功能:
  # 使用特定模板和主题
  remup example.ru -o output --template academic --theme dark
  
  # 启用HTML压缩
  remup example.ru -o output --minify
  
  # 禁用注卡生成
  remup example.ru -o output --no-vibes
  
  # 生成详细统计信息
  remup example.ru -o output --stats
        """
    )
    
    # 输入参数
    parser.add_argument(
        "inputs", 
        nargs="*",
        help="输入的.ru文件或目录（可指定多个）"
    )
    
    # 输出参数
    parser.add_argument(
        "-o", "--output", 
        default="./output",
        help="输出目录 (默认: ./output)"
    )
    parser.add_argument(
        "-t", "--title", 
        help="页面标题（单个文件）"
    )
    parser.add_argument(
        "--title-prefix", 
        help="标题前缀（批量编译时使用）"
    )
    
    # 功能选项
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="显示详细输出"
    )
    parser.add_argument(
        "--version", 
        action="version",
        version=f"RemUp编译器 v{__version__}"
    )
    parser.add_argument(
        "--config", 
        help="使用配置文件（JSON格式）"
    )
    parser.add_argument(
        "--batch", 
        action="store_true",
        help="批量编译模式"
    )
    
    # 高级选项
    parser.add_argument(
        "--template", 
        default="default",
        choices=["default", "academic", "minimal", "card-based"],
        help="模板样式 (默认: default)"
    )
    parser.add_argument(
        "--theme", 
        default="light",
        choices=["light", "dark", "warm"],
        help="主题样式 (默认: light)"
    )
    parser.add_argument(
        "--minify", 
        action="store_true",
        help="压缩生成的HTML"
    )
    parser.add_argument(
        "--no-vibes", 
        action="store_true",
        help="禁用注卡生成"
    )
    parser.add_argument(
        "--no-index", 
        action="store_true",
        help="不生成索引文件"
    )
    parser.add_argument(
        "--stats", 
        action="store_true",
        help="生成编译统计信息"
    )
    parser.add_argument(
        "--clean", 
        action="store_true",
        help="清理输出目录（如果存在）"
    )
    
    args = parser.parse_args()
    
    # 显示版本信息
    print(f"🎴 RemUp编译器 v{__version__}")
    print("=" * 60)
    
    try:
        # 加载配置（如果指定）
        config = {}
        if args.config:
            config = load_config_file(Path(args.config))
            if args.verbose:
                print(f"📋 加载配置文件: {args.config}")
        
        # 创建编译器实例
        compiler = RemUpCompiler(verbose=args.verbose)
        
        # 处理输入
        if args.config and not args.inputs:
            # 使用配置文件进行批量编译
            if args.verbose:
                print("🔄 使用配置文件进行批量编译")
            result = compiler.batch_compile(config)
            print_result_stats(result, args.verbose)
            
        elif args.batch or len(args.inputs) > 1:
            # 批量编译模式
            if args.verbose:
                print(f"📁 批量编译模式: {len(args.inputs)} 个输入")
            
            batch_config = {
                "inputs": args.inputs,
                "output": args.output,
                "title_prefix": args.title_prefix,
                "clean_output": args.clean,
                "continue_on_error": True,
                "generate_index": not args.no_index,
                "copy_static": True
            }
            
            # 合并配置文件
            batch_config.update(config)
            
            result = compiler.batch_compile(batch_config)
            print_result_stats(result, args.verbose)
            
        elif args.inputs:
            # 单个文件或目录编译
            input_path = Path(args.inputs[0])
            
            if input_path.is_file() and input_path.suffix in ['.ru', '.rem']:
                # 编译单个文件
                if args.verbose:
                    print(f"📄 编译单个文件: {input_path}")
                
                result = compiler.compile_file(
                    input_path, 
                    Path(args.output), 
                    args.title
                )
                print(f"✅ 编译完成: {result}")
                
            elif input_path.is_dir():
                # 编译目录
                if args.verbose:
                    print(f"📁 编译目录: {input_path}")
                
                results = compiler.compile_directory(
                    input_path, 
                    Path(args.output), 
                    args.title_prefix or args.title
                )
                print(f"✅ 编译完成: {len(results)} 个文件")
                
                if args.verbose:
                    for result in results:
                        print(f"   📄 {result.relative_to(Path(args.output))}")
                        
            else:
                print(f"❌ 错误: 输入路径不存在或不是.ru文件: {input_path}")
                return 1
                
        else:
            print("❌ 错误: 请指定输入文件或目录")
            parser.print_help()
            return 1
            
    except Exception as e:
        print(f"❌ 编译错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def load_config_file(config_path: Path) -> dict:
    """加载配置文件"""
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_result_stats(result: dict, verbose: bool = False):
    """打印编译结果统计"""
    print("\n" + "=" * 60)
    print("📊 编译统计")
    print("=" * 60)
    
    total = result.get('total_files', 0)
    successful = result.get('successful', 0)
    failed = result.get('failed', 0)
    
    print(f"📁 输出目录: {result.get('output_dir', 'N/A')}")
    print(f"⏰ 编译时间: {result.get('timestamp', 'N/A')}")
    print(f"📄 文件统计: 成功 {successful} / 失败 {failed} / 总计 {total}")
    
    if verbose and 'generated_files' in result:
        print(f"\n📋 生成的文件:")
        for file_path in result['generated_files'][:10]:  # 只显示前10个
            print(f"   📄 {file_path}")
        
        if len(result['generated_files']) > 10:
            print(f"   ... 还有 {len(result['generated_files']) - 10} 个文件")
    
    if failed > 0:
        print(f"⚠️  注意: {failed} 个文件编译失败")
    else:
        print("🎉 所有文件编译成功!")


class Config:
    """配置类 - 用于创建编译配置"""
    
    @staticmethod
    def create_sample() -> dict:
        """创建示例配置文件"""
        return {
            "compiler": {
                "verbose": True,
                "template_dir": "templates",
                "static_dir": "static"
            },
            "defaults": {
                "output": "./dist",
                "template": "academic",
                "theme": "light",
                "enable_vibes": True,
                "minify_html": False,
                "generate_index": True
            },
            "projects": [
                {
                    "name": "学习笔记",
                    "inputs": ["notes/"],
                    "output": "dist/notes",
                    "title_prefix": "学习笔记"
                },
                {
                    "name": "示例文档", 
                    "inputs": ["examples/"],
                    "output": "dist/examples",
                    "template": "minimal"
                }
            ]
        }


def init_project(project_dir: Path = None):
    """初始化RemUp项目"""
    if project_dir is None:
        project_dir = Path.cwd()
    
    # 创建目录结构
    directories = [
        "notes",
        "templates",
        "static/css",
        "static/js",
        "static/images",
        "output"
    ]
    
    for dir_name in directories:
        (project_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    # 创建示例配置文件
    config = Config.create_sample()
    config_path = project_dir / "remup.config.json"
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 创建示例笔记
    example_note = """--<示例归档>--
# 这是一个示例RemUp文档
# 使用 `注卡语法`[这是一个注卡示例] 来创建知识点链接

<+欢迎使用RemUp
(!: 重要)
(>: #markdown, #学习笔记, 相关技术)

---介绍
RemUp是一个基于卡片的学习笔记系统，支持：

`注卡系统`[通过反引号创建知识点链接] >> 创建知识点之间的关联
`模板系统`[多种输出样式] >> 支持学术、简约等样式
`归档管理`[按主题组织内容] >> 保持内容结构化

---快速开始
1. 创建 `.ru` 文件
2. 使用RemUp语法编写内容
3. 运行 `remup 文件名.ru` 编译

---示例代码
```python
def hello_remup():
'''欢迎函数'''
print("Hello RemUp!")
/+

<+注卡示例
(i: 示例)

---说明
这是一个`注卡`[相互关联的知识点]的示例。

当你在内容中使用 `反引号包裹文本`[后面跟方括号批注] 时，
RemUp会自动为这些内容生成详细的知识卡片。

---优势
- `知识点关联`[建立知识网络] >> 帮助记忆和理解
- `批注系统`[添加详细解释] >> 提供上下文信息
- `自动生成`[智能创建卡片] >> 减少手动工作
/+
"""
    
    example_path = project_dir / "notes" / "示例笔记.ru"
    try:
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_note)
        print(f"📝 创建示例笔记: {example_path.relative_to(project_dir)}")
    except Exception as e:
        print(f"⚠️  示例笔记创建失败: {e}")
    
    # 创建README
    readme = f"""# RemUp 项目

这是一个使用RemUp编译器的学习笔记项目。

## 项目结构
```
{project_dir.name}/
├── notes/           # 存放.ru笔记文件
├── templates/       # 自定义模板（可选）
├── static/          # 静态资源（可选）
├── output/          # 编译输出
└── remup.config.json  # 配置文件
```
## 快速开始

1. 编辑 `notes/示例笔记.ru` 文件
2. 运行编译命令：
```bash
remup notes/示例笔记.ru -o output
```
3. 查看生成的HTML文件：`output/示例笔记.html`

## 配置说明

编辑 `remup.config.json` 文件来自定义编译选项。

## 更多信息

访问 RemUp文档 了解更多语法和功能。
"""
    readme_path = project_dir / "README.md"
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        print(f"📄 创建README: {readme_path.relative_to(project_dir)}")
    except Exception as e:
        print(f"⚠️  README创建失败: {e}")
    
    # 创建基础模板文件
    base_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <title>{{ page_title }} - RemUp</title>
 <style>
     /* 基础样式 */
     body {{
         font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
         max-width: 1000px;
         margin: 0 auto;
         padding: 20px;
         line-height: 1.6;
     }}
     .card {{
         background: white;
         border-radius: 8px;
         padding: 20px;
         margin: 20px 0;
         box-shadow: 0 2px 10px rgba(0,0,0,0.1);
     }}
 </style>
</head>
<body>
 <h1>{{ page_title }}</h1>
 {% for archive in archives %}
 <div class="archive">
     <h2>{{ archive.name }}</h2>
     {% for card in archive.cards %}
     <div class="card">
         <h3>{{ card.theme }}</h3>
         <!-- 卡片内容 -->
     </div>
     {% endfor %}
 </div>
 {% endfor %}
</body>
</html>"""
 
    template_path = project_dir / "templates" / "base.html"
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(base_template)
        print(f"🎨 创建基础模板: {template_path.relative_to(project_dir)}")
    except Exception as e:
        print(f"⚠️  模板创建失败: {e}")
    
    # 创建基础CSS
    css_content = """/* RemUp基础样式 */
body {
 font-family: Arial, sans-serif;
 line-height: 1.6;
 margin: 0;
 padding: 20px;
 background: #f5f5f5;
}
.card {
 background: white;
 border-radius: 8px;
 padding: 20px;
 margin: 15px 0;
 box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}"""
 
    css_path = project_dir / "static" / "css" / "style.css"
    try:
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        print(f"🎨 创建基础样式: {css_path.relative_to(project_dir)}")
    except Exception as e:
        print(f"⚠️  样式文件创建失败: {e}")
    
    print("\\n" + "="*50)
    print("✅ 项目初始化完成!")
    print("="*50)
    print(f"📁 项目目录: {project_dir.absolute()}")
    print("📝 示例文件: notes/示例笔记.ru")
    print("⚙️  配置文件: remup.config.json")
    print("\\n🚀 开始使用:")
    print(f"  cd {project_dir}")
    print("  remup notes/示例笔记.ru -o output")
    print("\\n💡 提示: 编辑 notes/示例笔记.ru 文件开始编写您的内容")


def setup_init_parser(subparsers):
    """设置init命令解析器"""
    init_parser = subparsers.add_parser(
        'init', 
        help='初始化新的RemUp项目'
    )
    init_parser.add_argument(
        'directory', 
        nargs='?', 
        default='.',
        help='项目目录（默认: 当前目录）'
    )
    init_parser.add_argument(
        '--force',
        action='store_true',
        help='强制初始化，覆盖现有文件'
    )
    return init_parser


def main():
    """主函数"""
    # 检查是否有init命令
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        # 处理init命令
        init_parser = argparse.ArgumentParser(
            description='初始化RemUp项目',
            prog='remup init'
        )
        init_parser.add_argument(
            'directory', 
            nargs='?', 
            default='.',
            help='项目目录（默认: 当前目录）'
        )
        init_parser.add_argument(
            '--force',
            action='store_true',
            help='强制初始化，覆盖现有文件'
        )
        
        # 只解析init相关的参数
        init_args = sys.argv[2:]
        try:
            args = init_parser.parse_args(init_args)
        except SystemExit:
            # 解析错误时显示帮助信息
            init_parser.print_help()
            return 1
        
        project_dir = Path(args.directory).resolve()
        
        try:
            # 检查目录是否已存在且有内容
            if project_dir.exists() and any(project_dir.iterdir()) and not args.force:
                print(f"⚠️  目录 '{project_dir}' 不为空，使用 --force 覆盖")
                return 1
                
            init_project(project_dir)
            return 0
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            if '--verbose' in sys.argv or '-v' in sys.argv:
                import traceback
                traceback.print_exc()
            return 1

    # 正常编译命令处理
    parser = argparse.ArgumentParser(
        description=f"RemUp编译器 - 将.ru文件编译为HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    示例:
    remup example.ru                    # 编译单个文件
    remup example.ru -o output          # 指定输出目录
    remup example.ru -t "我的笔记"       # 指定页面标题
    remup examples/ -o docs            # 编译整个目录
    remup init                         # 初始化新项目
    remup init my_project              # 在指定目录初始化
        """
    )
    
    # 添加编译相关参数
    parser.add_argument("input", nargs='?', help="输入的.ru文件或包含.ru文件的目录")
    parser.add_argument("-o", "--output", default="./output", 
                    help="输出目录 (默认: ./output)")
    parser.add_argument("-t", "--title", help="HTML页面标题")
    parser.add_argument("-v", "--verbose", action="store_true",
                    help="显示详细输出")
    parser.add_argument("--version", action="store_true",
                    help="显示版本信息")

    # 解析参数
    args = parser.parse_args()

    # 显示版本信息
    if args.version:
        print(f"RemUp编译器 v{__version__}")
        return 0

    # 如果没有输入文件，显示帮助
    if not args.input:
        parser.print_help()
        return 0

    print(f"🎴 RemUp编译器 v{__version__}")
    print("=" * 50)

    # 创建编译器实例
    compiler = RemUpCompiler(verbose=args.verbose)

    try:
        input_path = Path(args.input)
        output_dir = Path(args.output)
        
        if input_path.is_file() and input_path.suffix in ['.ru', '.rem']:
            # 编译单个文件
            result = compiler.compile_file(input_path, output_dir, args.title)
            print(f"✅ 编译完成: {result}")
            
        elif input_path.is_dir():
            # 编译目录
            results = compiler.compile_directory(input_path, output_dir, args.title)
            print(f"✅ 编译完成 {len(results)} 个文件")
            for result in results:
                print(f"   📄 {result}")
                
        else:
            print(f"❌ 错误: 输入路径不存在或不是.ru文件: {input_path}")
            return 1
            
    except Exception as e:
        print(f"❌ 编译错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())