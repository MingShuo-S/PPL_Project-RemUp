"""
RemUp编译器包
"""

__version__ = "1.0.0"
__author__ = "MingShuo_S"
__email__ = "2954809209@qq.com"

# 导入主要组件
from .compiler import RemUpCompiler, CompileConfig, CompileResult
from .parser import RemUpParser, VibeCardProcessor
from .html_generator import HTMLGenerator
from .template_engine import AdvancedTemplateEngine, SimpleTemplateEngine
from .ast_nodes import Document, Archive, MainCard, Label, Region, VibeCard, VibeArchive

# 导入工具类
from .utils import (
    RemUpLogger,
    FileUtils,
    TextUtils, 
    ConfigUtils,
    ValidationUtils,
    PerformanceUtils,
    get_version,
    get_timestamp,
    format_file_size,
    create_backup
)

# 导出主要类
__all__ = [
    'RemUpCompiler',
    'CompileConfig', 
    'CompileResult',
    'RemUpParser',
    'VibeCardProcessor', 
    'HTMLGenerator',
    'AdvancedTemplateEngine',
    'SimpleTemplateEngine',
    'Document',
    'Archive', 
    'MainCard',
    'Label',
    'Region',
    'VibeCard', 
    'VibeArchive',
    'RemUpLogger',
    'FileUtils',
    'TextUtils',
    'ConfigUtils', 
    'ValidationUtils',
    'PerformanceUtils'
]

# 版本信息
def get_version():
    """获取版本信息"""
    return __version__

def get_info():
    """获取模块信息"""
    return {
        "name": "RemUp Compiler",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": "将.ru文件编译为HTML学习笔记"
    }