"""RemUp编译器 - 将RemUp标记语言(.ru文件)转换为HTML"""

from .compiler import compile_remup, Compiler
from .html_generator import HTMLGenerator
from .parser import Parser
from .lexer import Lexer

# 从ast_nodes中导入主要的类和函数
from .ast_nodes import (
    Document, Archive, MainCard, Region, Label, 
    VibeCard, Inline_Explanation, Rem_List, Code_Block, VibeArchive
)

__version__ = "1.0.0"
__author__ = "MingShuo_S"
__email__ = "2954809209@qq.com"

# 定义包的公共API接口
__all__ = [
    # 主要功能类和函数
    "compile_remup",
    "Compiler",
    "HTMLGenerator", 
    "Parser",
    "Lexer",
    
    # AST节点类
    "Document", "Archive", "MainCard", "Region", "Label",
    "VibeCard", "Inline_Explanation", "Rem_List", "Code_Block", "VibeArchive",
    
    # 元数据
    "__version__", "__author__", "__email__"
]

print(f"RemUp编译器 v{__version__} 已加载成功！支持文件格式: .ru, .remup")