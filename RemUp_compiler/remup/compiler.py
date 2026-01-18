"""RemUp编译器核心协调模块"""

from pathlib import Path
import os
from .lexer import Lexer
from .parser import Parser
from .html_generator import HTMLGenerator
from .ast_nodes import Document, Archive, MainCard, Region, Label, VibeCard, Inline_Explanation, Rem_List, Code_Block, VibeArchive

class RemUpCompiler:
    """RemUp编译器主类"""
    
    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {'.ru', '.remup'}  # 同时支持.ru和.remup
    
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser([], "")
        self.generator = HTMLGenerator()
    
    def compile_file(self, input_file, output_file=None, css_file=None):
        """编译RemUp文件为HTML - 修复路径问题"""
        
        # 读取源文件
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print("=== 源代码内容 ===")
        print(repr(source_code))
        
        # 执行编译流程
        lexer = Lexer()
        tokens = lexer.tokenize(source_code)
        
        print("=== 词法分析结果 ===")
        for i, token in enumerate(tokens[:20]):
            print(f"{i}: {token}")
        
        parser = Parser(tokens, str(input_file))
        ast = parser.parse()
        
        print("=== AST结构 ===")
        def print_simple_ast(node, indent=0):
            indent_str = "  " * indent
            if isinstance(node, Document):
                print(f"{indent_str}Document: {node.title}")
                print(f"{indent_str}Archives: {len(node.archives)}")
                if node.vibe_archive:
                    print(f"{indent_str}VibeArchive: {len(node.vibe_archive.cards)} cards")
            elif isinstance(node, Archive):
                print(f"{indent_str}Archive: {node.name} ({len(node.cards)} cards)")
            elif isinstance(node, MainCard):
                print(f"{indent_str}MainCard: {node.theme}")
        
        print_simple_ast(ast)
        
        # 修复输出路径处理
        if output_file is None:
            # 使用输入文件名（不含扩展名）作为输出文件名
            input_path = Path(input_file)
            output_file = input_path.with_suffix('.html')
            # 确保输出目录存在
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / output_file.name
        
        print(f"=== 输出路径 ===")
        print(f"输出文件: {output_file}")
        
        # 处理CSS
        css_content = None
        if css_file and Path(css_file).exists():
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
        
        generator = HTMLGenerator()
        
        # 关键修复：确保传递正确的文件名
        result_path = generator.generate(ast, str(output_file), css_content)
        
        print(f"✅ 编译成功: {input_file} -> {result_path}")
        return result_path
    
    def compile_directory(self, input_dir, output_dir=None, css_file=None):
        """
        编译目录下的所有.ru文件
        """
        input_path = Path(input_dir)
        if output_dir is None:
            output_dir = input_path / "output"
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        compiled_files = []
        for file_path in input_path.glob("*.ru"):
            output_file = output_path / file_path.with_suffix(".html").name
            result = self.compile_file(file_path, output_file, css_file)
            compiled_files.append(result)
        
        return compiled_files

def compile_remup(input_file, output_file=None, css_file=None):
    """编译RemUp文件为HTML - 添加调试信息"""
    
    # 读取源文件
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    print("=== 源代码内容 ===")
    print(repr(source_code))
    
    # 执行编译流程
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    
    print("=== 词法分析结果 ===")
    for i, token in enumerate(tokens[:20]):  # 只显示前20个token
        print(f"{i}: {token}")
    
    parser = Parser(tokens, str(input_file))
    ast = parser.parse()
    
    print("=== AST结构 ===")
    # 添加一个简单的AST打印函数
    def print_simple_ast(node, indent=0):
        indent_str = "  " * indent
        if isinstance(node, Document):
            print(f"{indent_str}Document: {node.title}")
            print(f"{indent_str}Archives: {len(node.archives)}")
            if node.vibe_archive:
                print(f"{indent_str}VibeArchive: {len(node.vibe_archive.cards)} cards")
        elif isinstance(node, Archive):
            print(f"{indent_str}Archive: {node.name} ({len(node.cards)} cards)")
        elif isinstance(node, MainCard):
            print(f"{indent_str}MainCard: {node.theme}")
    
    print_simple_ast(ast)
    
    # 继续正常的HTML生成流程...