#!/usr/bin/env python3
"""
RemUp编译器 v3.1 - 修复方法缺失问题
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from remup.parser import Parser
from remup.lexer import Lexer
from remup.html_generator import HTMLGenerator

class Compiler:
    """RemUp编译器 - 协调编译流程"""
    
    def __init__(self, project_root: str = None):
        """
        初始化编译器
        
        Args:
            project_root: 项目根目录，用于查找静态资源
        """
        # 检测项目根目录
        self.project_root = self._detect_project_root(project_root)
        self.html_generator = HTMLGenerator(project_root=str(self.project_root))
        
        print(f"🔧 编译器初始化完成")
        print(f"📁 项目根目录: {self.project_root}")
    
    def _detect_project_root(self, project_root: str = None) -> Path:
        """
        检测项目根目录
        
        Args:
            project_root: 用户指定的项目根目录
            
        Returns:
            检测到的项目根目录Path对象
        """
        # 如果用户指定了项目根目录，直接使用
        if project_root:
            root_path = Path(project_root)
            if (root_path / "static" / "css").exists():
                return root_path
            else:
                print(f"⚠️ 指定目录无static/css: {root_path}")
        
        # 自动检测项目根目录
        possible_roots = [
            # 1. 当前工作目录
            Path.cwd(),
            # 2. 脚本文件所在目录的父目录（编译器在remup包内）
            Path(__file__).parent.parent,
            # 3. 环境变量指定的目录
            Path(os.environ.get('REMUP_PROJECT_ROOT', '')),
        ]
        
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
    
    def compile(self, input_path: str, output_path: str = None, 
                theme: str = "RemStyle", page_title: str = None) -> str:
        """
        编译RemUp文件为HTML
        """
        print(f"🔨 开始编译: {input_path}")
        print(f"🎨 使用主题: {theme}")
        
        # 验证输入文件
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 自动生成输出路径
        if output_path is None:
            output_path = input_path.with_suffix('.html')
        else:
            output_path = Path(output_path)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取源代码
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 词法分析和语法分析
        lexer = Lexer()
        tokens = lexer.tokenize(source_code)
        parser = Parser(tokens)
        document = parser.parse()
        
        # 生成HTML
        result_path = self.html_generator.generate(
            document=document,
            output_path=str(output_path),
            theme=theme,
            page_title=page_title
        )
        
        # 打印编译摘要
        self._print_compilation_summary(document, result_path, theme)
        
        return result_path
    
    def compile_directory(self, input_dir: str, output_dir: str = None,
                         theme: str = "RemStyle", recursive: bool = False) -> List[str]:
        """
        编译目录中的所有RemUp文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录（可选）
            theme: 主题名称
            recursive: 是否递归处理子目录
            
        Returns:
            成功编译的文件路径列表
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = input_dir / "html_output"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 查找RemUp文件
        pattern = "**/*.remup" if recursive else "*.remup"
        remup_files = list(input_dir.glob(pattern))
        
        if not remup_files:
            print(f"⚠️ 在目录 {input_dir} 中未找到 .remup 文件")
            return []
        
        print(f"📁 发现 {len(remup_files)} 个RemUp文件")
        
        compiled_files = []
        for remup_file in remup_files:
            try:
                # 保持目录结构
                relative_path = remup_file.relative_to(input_dir)
                output_file = output_dir / relative_path.with_suffix('.html')
                
                # 确保输出子目录存在
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 编译文件
                result_path = self.compile(
                    input_path=str(remup_file),
                    output_path=str(output_file),
                    theme=theme
                )
                compiled_files.append(result_path)
                
            except Exception as e:
                print(f"❌ 编译失败 {remup_file}: {e}")
                continue
        
        print(f"✅ 成功编译 {len(compiled_files)}/{len(remup_files)} 个文件")
        return compiled_files
    
    def list_available_themes(self) -> List[str]:
        """列出所有可用的主题"""
        return self.html_generator.get_available_themes()
    
    def _print_compilation_summary(self, document, output_path: str, theme: str):
        """打印编译摘要"""
        total_cards = sum(len(archive.cards) for archive in document.archives)
        total_vibe_cards = 0
        for archive in document.archives:
            for card in archive.cards:
                total_vibe_cards += len(card.vibe_cards)
        
        print("=" * 60)
        print("🎉 编译完成!")
        print("=" * 60)
        print(f"📁 输出文件: {output_path}")
        print(f"🎨 使用主题: {theme}")
        print(f"📂 归档数量: {len(document.archives)}")
        print(f"🃏 卡片总数: {total_cards}")
        print(f"💡 注卡数量: {total_vibe_cards}")
        print(f"📋 注卡归档: {'✅ 有' if document.vibe_archive else '❌ 无'}")
        print("=" * 60)
        
        # 显示可用主题
        available_themes = self.list_available_themes()
        if len(available_themes) > 1:
            print("🎨 可用主题: " + ", ".join(available_themes))
            print("💡 使用 -t 参数切换主题，例如: -t DarkTheme")
            print("=" * 60)

def compile_remup(input_path: str, output_path: str = None, 
                 theme: str = "RemStyle", page_title: str = None) -> str:
    """
    便捷函数：编译单个RemUp文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        theme: 主题名称
        page_title: 自定义页面标题
        
    Returns:
        输出文件路径
    """
    compiler = Compiler()
    return compiler.compile(input_path, output_path, theme, page_title)

def compile_remup_directory(input_dir: str, output_dir: str = None,
                          theme: str = "RemStyle", recursive: bool = False) -> List[str]:
    """
    便捷函数：编译目录中的RemUp文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        theme: 主题名称
        recursive: 是否递归处理子目录
        
    Returns:
        成功编译的文件路径列表
    """
    compiler = Compiler()
    return compiler.compile_directory(input_dir, output_dir, theme, recursive)

if __name__ == "__main__":
    # 命令行测试
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        try:
            result = compile_remup(input_file)
            print(f"✅ 编译成功: {result}")
        except Exception as e:
            print(f"❌ 编译失败: {e}")
    else:
        print("用法: python compiler.py <input_file.remup>")