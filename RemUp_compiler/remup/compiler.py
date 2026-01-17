"""
RemUp编译器 - 完整功能版 (更新版)
支持新模板系统、注卡链接、高级配置等完整功能
"""

import re
import os
import shutil
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from .utils import (
    RemUpLogger, 
    FileUtils, 
    TextUtils, 
    ConfigUtils,
    ValidationUtils
)

# 导入解析器组件
try:
    from .parser import RemUpParser, VibeCardProcessor
    from .html_generator import HTMLGenerator
    from .ast_nodes import Document, Archive, MainCard, Label, Region, VibeCard, VibeArchive
except ImportError:
    # 简化回退
    from .parser import Parser as RemUpParser
    from .parser import VibeCardProcessor
    from .html_generator import SimpleHTMLGenerator as HTMLGenerator
    from .ast_nodes import Document, Archive, MainCard

@dataclass
class CompileResult:
    """编译结果"""
    main_file: Path
    vibe_files: List[Path]
    stats: Dict[str, Any]

@dataclass
class CompileConfig:
    """编译配置数据类"""
    input_path: Path
    output_dir: Path
    title: Optional[str] = None
    template: str = "default"
    theme: str = "light"
    enable_vibes: bool = True
    generate_index: bool = True
    copy_static: bool = True
    minify_html: bool = False
    custom_css: Optional[str] = None
    template_variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.template_variables is None:
            self.template_variables = {}

class RemUpCompiler:
    """
    RemUp编译器完整版 - 支持新模板系统
    """
    
    def __init__(self, verbose: bool = False, config_file: Optional[Path] = None,
                 template_dir: str = "templates", static_dir: str = "static"):
        self.verbose = verbose
        self.logger = RemUpLogger(verbose=verbose)  # 使用新的日志记录器
        self.config = self._load_config(config_file)
        # 使用新的工具类
        self.file_utils = FileUtils()
        self.text_utils = TextUtils()
        self.validation_utils = ValidationUtils()
        # 初始化组件 - 使用新的HTML生成器
        self.parser = RemUpParser(verbose=verbose)
        self.vibe_processor = VibeCardProcessor()
        self.html_generator = HTMLGenerator(template_dir, static_dir)
        
        # 统计信息
        self.compile_stats = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "start_time": datetime.now(),
            "errors": []
        }
        
        if verbose:
            print("🚀 RemUp编译器完整版初始化完成")
            print(f"   模板目录: {template_dir}")
            print(f"   静态资源: {static_dir}")
    
    def _load_config(self, config_file: Optional[Path]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "templates_dir": "templates",
            "static_dir": "static",
            "default_theme": "light",
            "enable_analytics": False,
            "auto_minify": True,
            "backup_compiled": True,
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "available_templates": ["default", "academic", "minimal", "archive"]
        }
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ 配置文件加载失败: {e}")
        
        return default_config
    
    def compile_file(self, input_file: Path, output_dir: Path, 
                    title: Optional[str] = None, **kwargs) -> CompileResult:
        """
        编译单个文件 - 支持新模板系统
        """
        # 创建编译配置
        config = CompileConfig(
            input_path=input_file,
            output_dir=output_dir,
            title=title,
            **kwargs
        )
        
        if self.verbose:
            print("=" * 60)
            print(f"📄 编译文件: {input_file}")
            print(f"   输出目录: {output_dir}")
            print(f"   标题: {title or '自动生成'}")
            print(f"   模板: {config.template}")
            print(f"   主题: {config.theme}")
        
        # 验证输入文件
        self._validate_input_file(input_file)
        
        # 准备输出目录
        self._prepare_output_dir(output_dir)
        
        # 读取源文件
        source_code = self._read_source_file(input_file)
        
        # 解析语法
        document_ast = self._parse_source_code(source_code, config)
        
        # 处理注卡系统
        if config.enable_vibes:
            document_ast = self._process_vibe_cards(document_ast, config)
        
        # 生成HTML - 使用新的HTML生成器
        result = self._generate_html_with_new_system(document_ast, config)
        
        # 后处理
        self._post_process(result, config)
        
        if self.verbose:
            print("✅ 编译完成!")
            print(f"   主文件: {result.main_file}")
            if result.vibe_files:
                print(f"   注卡文件: {len(result.vibe_files)}个")
        
        return result
    
    def compile_directory(self, input_dir: Path, output_dir: Path, 
                         title_prefix: Optional[str] = None, **kwargs) -> List[CompileResult]:
        """
        编译目录中的所有.ru文件
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        # 查找所有.ru文件
        ru_files = list(input_dir.glob("**/*.ru"))
        if not ru_files:
            raise ValueError(f"在目录 {input_dir} 中未找到.ru文件")
        
        if self.verbose:
            print("📁 编译目录")
            print(f"   输入目录: {input_dir}")
            print(f"   输出目录: {output_dir}")
            print(f"   找到 {len(ru_files)} 个.ru文件")
        
        results = []
        successful = 0
        failed = 0
        
        for ru_file in ru_files:
            try:
                # 为每个文件创建对应的输出子目录结构
                relative_path = ru_file.relative_to(input_dir)
                file_output_dir = output_dir / relative_path.parent
                
                # 使用文件名为标题
                file_title = title_prefix + " - " + ru_file.stem if title_prefix else ru_file.stem
                
                result = self.compile_file(ru_file, file_output_dir, file_title, **kwargs)
                results.append(result)
                successful += 1
                
                if self.verbose:
                    print(f"   ✅ {relative_path}")
                    
            except Exception as e:
                failed += 1
                if self.verbose:
                    print(f"   ❌ {relative_path}: {e}")
                continue
        
        if self.verbose:
            print(f"📊 编译统计: 成功 {successful}, 失败 {failed}")
        
        return results
    
    def batch_compile(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量编译 - 支持新模板系统
        """
        if self.verbose:
            print("🔄 开始批量编译")
            print(f"   配置: {config}")
        
        # 获取输入列表
        inputs = config.get("inputs", [])
        output_dir = Path(config.get("output", "output"))
        title_prefix = config.get("title_prefix")
        clean_output = config.get("clean_output", False)
        continue_on_error = config.get("continue_on_error", True)
        
        # 清理输出目录（如果需要）
        if clean_output and output_dir.exists():
            if self.verbose:
                print("🧹 清理输出目录...")
            shutil.rmtree(output_dir)
        
        # 处理所有输入
        all_results = []
        successful = 0
        failed = 0
        
        for input_path in inputs:
            input_path = Path(input_path)
            
            try:
                if input_path.is_file() and input_path.suffix == '.ru':
                    # 编译单个文件
                    result = self.compile_file(input_path, output_dir, title_prefix, **config)
                    all_results.append(result)
                    successful += 1
                    
                elif input_path.is_dir():
                    # 编译目录
                    results = self.compile_directory(input_path, output_dir, title_prefix, **config)
                    all_results.extend(results)
                    successful += len(results)
                    
                else:
                    if self.verbose:
                        print(f"   ⚠️  跳过: {input_path} (不是.ru文件或目录)")
                    
            except Exception as e:
                failed += 1
                if self.verbose:
                    print(f"   ❌ {input_path}: {e}")
                
                if not continue_on_error:
                    raise
        
        # 生成索引文件（如果有多个输出）
        if len(all_results) > 1 and config.get("generate_index", True):
            try:
                index_file = self._generate_index_file(all_results, output_dir, title_prefix)
                if self.verbose:
                    print(f"   生成索引文件: {index_file}")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  索引文件生成失败: {e}")
        
        # 返回统计结果
        result_stats = {
            "total_files": len(all_results),
            "successful": successful,
            "failed": failed,
            "output_dir": str(output_dir),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.verbose:
            print("📊 批量编译完成")
            print(f"   成功: {successful}, 失败: {failed}, 总计: {len(all_results)}")
        
        return result_stats
    
    def _validate_input_file(self, input_file: Path):
        """验证输入文件"""
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        if input_file.suffix not in ['.ru', '.rem', '.rup']:
            raise ValueError(f"不支持的文件格式: {input_file.suffix}")
        
        # 检查文件大小
        file_size = input_file.stat().st_size
        max_size = self.config.get("max_file_size", 10 * 1024 * 1024)
        if file_size > max_size:
            raise ValueError(f"文件过大: {file_size}字节 > {max_size}字节限制")
    
    def _prepare_output_dir(self, output_dir: Path):
        """准备输出目录"""
        output_dir.mkdir(parents=True, exist_ok=True)
    
    def _read_source_file(self, input_file: Path) -> str:
        """读取源文件"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            for encoding in ['gbk', 'latin-1']:
                try:
                    with open(input_file, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"无法解码文件: {input_file}")
    
    def _parse_source_code(self, source_code: str, config: CompileConfig) -> Document:
        """解析源代码"""
        if self.verbose:
            print("🔍 解析RemUp语法...")
        
        try:
            document_ast = self.parser.parse(source_code)
            
            # 验证AST结构
            self._validate_ast_structure(document_ast)
            
            if self.verbose:
                archives_count = len(document_ast.archives)
                cards_count = sum(len(archive.cards) for archive in document_ast.archives)
                print(f"   解析完成: {archives_count}个归档, {cards_count}张卡片")
            
            return document_ast
            
        except Exception as e:
            if self.verbose:
                print(f"❌ 解析错误: {e}")
            raise
    
    def _validate_ast_structure(self, document_ast: Document):
        """验证AST结构完整性"""
        if not document_ast.archives:
            raise ValueError("文档中没有归档")
        
        for archive in document_ast.archives:
            if not archive.cards:
                print(f"⚠️  归档 '{archive.name}' 中没有卡片")
            
            for card in archive.cards:
                if not card.theme.strip():
                    raise ValueError("卡片主题不能为空")
    
    def _process_vibe_cards(self, document_ast: Document, config: CompileConfig) -> Document:
        """处理注卡系统"""
        if self.verbose:
            print("💡 处理注卡系统...")
        
        try:
            # 基础注卡处理
            document_ast = self.vibe_processor.process(document_ast)
            
            # 高级注卡链接处理
            document_ast = self._enhance_vibe_links(document_ast)
            
            # 统计注卡信息
            vibe_stats = self._calculate_vibe_stats(document_ast)
            
            if self.verbose and vibe_stats['total_vibes'] > 0:
                print(f"   注卡处理完成: {vibe_stats['total_vibes']}个注卡")
                if vibe_stats['generated_cards'] > 0:
                    print(f"   生成 {vibe_stats['generated_cards']}张注卡主卡")
            
            return document_ast
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  注卡处理警告: {e}")
            return document_ast  # 注卡处理失败不影响主流程
    
    def _enhance_vibe_links(self, document_ast: Document) -> Document:
        """增强注卡链接关系"""
        # 收集所有注卡主题
        all_vibe_themes = set()
        if hasattr(document_ast, 'vibe_archive') and document_ast.vibe_archive:
            for card in document_ast.vibe_archive.cards:
                all_vibe_themes.add(card.theme.lower())
        
        # 在主卡中查找对注卡的引用并建立链接
        for archive in document_ast.archives:
            for card in archive.cards:
                for region in card.regions:
                    # 在区域内容中查找注卡引用
                    referenced_vibes = self._find_vibe_references(region.content, all_vibe_themes)
                    
                    # 添加引用标签
                    for vibe_theme in referenced_vibes:
                        ref_label = Label(
                            symbol="→",
                            content=[f"#{vibe_theme}"],
                            type="vibe_reference"
                        )
                        if ref_label not in card.labels:
                            card.labels.append(ref_label)
        
        return document_ast
    
    def _find_vibe_references(self, content: str, vibe_themes: set) -> List[str]:
        """在内容中查找注卡引用"""
        references = []
        
        for theme in vibe_themes:
            # 使用单词边界匹配，避免部分匹配
            pattern = r'\b' + re.escape(theme) + r'\b'
            if re.search(pattern, content, re.IGNORECASE):
                references.append(theme)
        
        return references
    
    def _calculate_vibe_stats(self, document_ast: Document) -> Dict[str, int]:
        """计算注卡统计信息"""
        stats = {
            'total_vibes': 0,
            'generated_cards': 0,
            'vibe_links': 0
        }
        
        # 计算主卡中的注卡数量
        for archive in document_ast.archives:
            for card in archive.cards:
                stats['total_vibes'] += len(getattr(card, 'vibe_cards', []))
                for region in card.regions:
                    stats['total_vibes'] += len(getattr(region, 'vibe_cards', []))
        
        # 计算生成的注卡主卡数量
        if hasattr(document_ast, 'vibe_archive') and document_ast.vibe_archive:
            stats['generated_cards'] = len(document_ast.vibe_archive.cards)
        
        return stats
    
    def _generate_html_with_new_system(self, document_ast: Document, config: CompileConfig) -> CompileResult:
        """使用新的HTML生成器生成HTML文档"""
        if self.verbose:
            print("🎨 生成HTML文档...")
        
        # 设置默认标题
        title = config.title or config.input_path.stem
        
        # 生成主HTML文件
        main_output_file = config.output_dir / f"{config.input_path.stem}.html"
        
        try:
            result_path = self.html_generator.generate(
                document_ast, 
                main_output_file, 
                title, 
                config.template
            )
        except Exception as e:
            if self.verbose:
                print(f"❌ HTML生成错误: {e}")
            raise
        
        # 生成注点HTML文件（如果有注点）
        vibe_files = []
        vibe_archive = getattr(document_ast, 'vibe_archive', None)
        if vibe_archive and hasattr(vibe_archive, 'cards') and vibe_archive.cards and config.enable_vibes:
            if self.verbose:
                print("📝 生成注点文档...")
            
            try:
                vibe_output_file = config.output_dir / f"{config.input_path.stem}_vibes.html"
                vibe_title = f"{title} - 注点生成"
                
                # 创建只包含注点的文档
                vibe_document = Document(archives=[vibe_archive])
                self.html_generator.generate(vibe_document, vibe_output_file, vibe_title, config.template)
                vibe_files.append(vibe_output_file)
                
                if self.verbose:
                    print(f"   注点文件: {vibe_output_file}")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  注点文件生成失败: {e}")
        
        # 计算统计信息
        stats = self._calculate_document_stats(document_ast)
        
        return CompileResult(
            main_file=result_path,
            vibe_files=vibe_files,
            stats=stats
        )
    
    def _calculate_document_stats(self, document_ast: Document) -> Dict[str, Any]:
        """计算文档统计信息"""
        total_cards = sum(len(archive.cards) for archive in document_ast.archives)
        total_regions = 0
        total_labels = 0
        
        for archive in document_ast.archives:
            for card in archive.cards:
                total_regions += len(card.regions)
                total_labels += len(card.labels)
        
        vibe_stats = self._calculate_vibe_stats(document_ast)
        
        return {
            'total_archives': len(document_ast.archives),
            'total_cards': total_cards,
            'total_regions': total_regions,
            'total_labels': total_labels,
            **vibe_stats
        }
    
    def _post_process(self, result: CompileResult, config: CompileConfig):
        """后处理"""
        # 复制静态资源
        if config.copy_static:
            self._copy_static_resources(config.output_dir)
        
        # 生成索引文件
        if config.generate_index:
            self._generate_index_file([result.main_file] + result.vibe_files, config.output_dir, config.title)
        
        # 更新统计信息
        self.compile_stats["successful"] += 1
        self.compile_stats["total_files"] += 1
    
    def _copy_static_resources(self, output_dir: Path):
        """复制静态资源"""
        # 这个功能现在由HTML生成器处理
        pass
    
    def _generate_index_file(self, html_files: List[Path], output_dir: Path, title: str) -> Path:
        """生成索引文件"""
        index_file = output_dir / "index.html"
        
        # 过滤掉索引文件自身
        html_files = [f for f in html_files if f != index_file]
        
        if len(html_files) <= 1:
            return index_file  # 只有一个文件不需要索引
        
        # 生成简单的索引HTML
        index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 索引</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px; 
            margin: 40px auto; 
            padding: 20px;
            background: #f5f7fa;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .file-list {{ 
            list-style: none; 
            padding: 0; 
            display: grid;
            gap: 10px;
        }}
        .file-item {{ 
            margin: 5px 0; 
        }}
        .file-link {{ 
            display: block;
            text-decoration: none; 
            color: #3498db;
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            border-left: 4px solid #3498db;
        }}
        .file-link:hover {{
            background: #3498db;
            color: white;
            transform: translateX(5px);
        }}
        .compile-info {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>RemUp编译器生成的文档索引</p>
    </div>
    
    <p>共 {len(html_files)} 个文档</p>
    <ul class="file-list">
        {"".join(f'<li class="file-item"><a href="{f.name}" class="file-link">{f.stem}</a></li>' 
                 for f in html_files)}
    </ul>
    
    <div class="compile-info">
        <p>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</body>
</html>"""
        
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_html)
        except Exception as e:
            if self.verbose:
                print(f"⚠️  索引文件写入失败: {e}")
        
        return index_file


# 简化版本 - 向后兼容
class SimpleRemUpCompiler(RemUpCompiler):
    """简化版RemUp编译器 - 向后兼容"""
    
    def compile_file(self, input_file: Path, output_dir: Path, 
                    title: Optional[str] = None) -> CompileResult:
        """简化版编译方法"""
        return super().compile_file(input_file, output_dir, title, template="default")


# 使用示例
if __name__ == "__main__":
    # 测试编译器
    compiler = RemUpCompiler(verbose=True)
    
    # 测试配置
    config = {
        "input_path": Path("example.ru"),
        "output_dir": Path("output"),
        "title": "测试文档",
        "template": "default",
        "theme": "light",
        "enable_vibes": True,
        "minify_html": False
    }
    
    try:
        # 创建测试文件
        test_code = """
--<测试归档>--
<+测试卡片
(!: 重要)
(>: #相关卡片, 示例)

---内容
这是一个`测试注卡`[这是一个测试注卡]的示例内容。
>> 这是一个行内解释示例

---代码示例
```python
def hello_remup():
'''欢迎函数'''
print("Hello RemUp!")
```
/+
"""
        
        test_file = Path("test_example.ru")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        # 编译测试
        result = compiler.compile_file(test_file, Path("test_output"), "测试文档")
        print(f"✅ 编译成功: {result}")
        
        # 清理测试文件
        test_file.unlink()
        shutil.rmtree("test_output", ignore_errors=True)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()