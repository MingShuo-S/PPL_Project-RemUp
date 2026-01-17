"""
完整的HTML生成器 - 与RemUp CSS样式完美匹配
支持academic、archive、base、footer、header、minimal等模板
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

class HTMLGenerator:
    """完整的HTML生成器 - 与RemUp CSS样式完美匹配"""
    
    def __init__(self, template_dir: str = "templates", static_dir: str = "static"):
        self.template_dir = Path(template_dir)
        self.static_dir = Path(static_dir)
    
        # 确保目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建默认模板（如果不存在）
        self._create_default_templates()
    
    def generate(self, document_ast, output_file: Path, title: str, 
                template: str = "default") -> Path:
        """
        生成HTML文档
        
        Args:
            document_ast: 文档AST
            output_file: 输出文件路径
            title: 页面标题
            template: 模板名称 (default, academic, minimal, archive)
            
        Returns:
            生成的HTML文件路径
        """
        # 准备上下文数据
        context = self._prepare_context(document_ast, title, template)
        
        # 获取模板内容
        template_content = self._get_template_content(template)
        
        # 渲染模板
        html_content = self._render_template(template_content, context)
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 复制静态资源
        self._copy_static_resources(output_file.parent)
        
        return output_file
    
    def _prepare_context(self, document_ast, title: str, template: str) -> Dict[str, Any]:
        """准备模板上下文数据"""
        # 处理主归档
        archives_data = []
        total_cards = 0
        total_vibe_cards = 0
        
        for archive in getattr(document_ast, 'archives', []):
            archive_data = self._convert_archive_to_dict(archive)
            archives_data.append(archive_data)
            total_cards += len(archive_data['cards'])
        
        # 处理注卡归档
        vibe_archive_data = None
        vibe_archive = getattr(document_ast, 'vibe_archive', None)
        if vibe_archive and getattr(vibe_archive, 'cards', []):
            vibe_archive_data = self._convert_archive_to_dict(vibe_archive)
            total_vibe_cards = len(vibe_archive_data['cards'])
        
        # 计算统计信息
        total_all_cards = total_cards + total_vibe_cards
        
        return {
            'page_title': title,
            'archives': archives_data,
            'vibe_archive': vibe_archive_data,
            'compile_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_cards': total_cards,
            'total_vibe_cards': total_vibe_cards,
            'total_all_cards': total_all_cards,
            'has_vibe_archive': vibe_archive_data is not None,
            'template': template,
            'version': '1.0.0'
        }
    
    def _convert_archive_to_dict(self, archive) -> Dict[str, Any]:
        """将归档对象转换为字典"""
        archive_data = {
            'id': self._slugify(getattr(archive, 'name', '')),
            'name': getattr(archive, 'name', '未命名归档'),
            'cards': [],
            'card_count': len(getattr(archive, 'cards', []))
        }
        
        for card in getattr(archive, 'cards', []):
            card_data = self._convert_card_to_dict(card)
            archive_data['cards'].append(card_data)
        
        return archive_data
    
    def _convert_card_to_dict(self, card) -> Dict[str, Any]:
        """将卡片对象转换为字典"""
        card_data = {
            'id': self._slugify(getattr(card, 'theme', '')),
            'theme': getattr(card, 'theme', '未命名卡片'),
            'labels': [],
            'regions': []
        }
        
        # 处理标签
        for label in getattr(card, 'labels', []):
            label_data = {
                'symbol': getattr(label, 'symbol', ''),
                'content': getattr(label, 'content', []),
                'type': getattr(label, 'label_type', 'default')
            }
            card_data['labels'].append(label_data)
        
        # 处理区域
        for region in getattr(card, 'regions', []):
            region_data = self._convert_region_to_dict(region, card_data['theme'])
            card_data['regions'].append(region_data)
        
        return card_data
    
    def _convert_region_to_dict(self, region, source_card: str) -> Dict[str, Any]:
        """将区域对象转换为字典，并处理注卡语法"""
        region_content = getattr(region, 'content', '')
        region_lines = getattr(region, 'lines', [])
        
        # 处理注卡语法：`内容`[批注]
        processed_content, vibe_cards = self._process_vibe_cards_in_text(
            region_content, source_card
        )
        
        # 处理行内解释：>>解释文本
        processed_content = self._process_inline_explanations(processed_content)
        
        region_data = {
            'name': getattr(region, 'name', ''),
            'content': processed_content,
            'raw_content': region_content,
            'lines': region_lines,
            'vibe_cards': vibe_cards
        }
        
        return region_data
    
    def _process_vibe_cards_in_text(self, text: str, source_card: str) -> tuple:
        """处理文本中的注卡语法，返回处理后的文本和注卡列表"""
        vibe_cards = []
        
        # 匹配注卡语法：`内容`[批注]
        pattern = r'`([^`]+)`\[([^\]]+)\]'
        
        def replace_vibe(match):
            content = match.group(1).strip()
            annotation = match.group(2).strip()
            
            # 创建注卡数据
            vibe_card = {
                'content': content,
                'annotation': annotation,
                'source_card': source_card,
                'id': f"vibe-{self._slugify(content)}-{len(vibe_cards)}"
            }
            vibe_cards.append(vibe_card)
            
            # 返回HTML标记 - 使用CSS中定义的类
            return f'<span class="annotation-container">' \
                   f'<span class="annotation">{content}</span>' \
                   f'<div class="annotation-popup">{annotation}</div>' \
                   f'</span>'
        
        # 替换所有注卡标记
        processed_text = re.sub(pattern, replace_vibe, text)
        
        return processed_text, vibe_cards
    
    def _process_inline_explanations(self, text: str) -> str:
        """处理行内解释语法：>>解释文本"""
        pattern = r'>>\s*([^\n<]+)'
        
        def replace_explanation(match):
            explanation = match.group(1).strip()
            return f'<span class="inline-explanation">{explanation}</span>'
        
        return re.sub(pattern, replace_explanation, text)
    
    def _slugify(self, text: str) -> str:
        """生成URL友好的slug"""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text
    
    def _get_template_content(self, template: str) -> str:
        """获取模板内容"""
        template_files = {
            'default': 'base.html',
            'academic': 'academic.html', 
            'minimal': 'minimal.html',
            'archive': 'archive.html'
        }
        
        template_file = template_files.get(template, 'base.html')
        template_path = self.template_dir / template_file
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 返回默认模板
            return self._get_default_template()
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """简单模板渲染"""
        result = template
        
        # 处理变量替换 {{ variable }}
        for key, value in context.items():
            placeholder = "{{ " + key + " }}"
            result = result.replace(placeholder, str(value))
        
        # 处理简单的if条件
        result = self._process_simple_conditions(result, context)
        
        return result
    
    def _process_simple_conditions(self, template: str, context: Dict[str, Any]) -> str:
        """处理简单的条件语句"""
        # 处理 {% if condition %} ... {% endif %}
        pattern = r'{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%\}'
        
        def replace_condition(match):
            condition = match.group(1)
            content = match.group(2)
            
            if context.get(condition):
                return content
            return ""
        
        return re.sub(pattern, replace_condition, template, flags=re.DOTALL)
    
    def _copy_static_resources(self, output_dir: Path) -> None:
        """复制静态资源到输出目录"""
        if not self.static_dir.exists():
            # 创建默认静态资源
            self._create_default_static_resources()
            return
        
        target_static_dir = output_dir / "static"
        target_static_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 复制整个静态目录
            if target_static_dir.exists():
                shutil.rmtree(target_static_dir)
            
            shutil.copytree(self.static_dir, target_static_dir)
        except Exception as e:
            print(f"⚠️ 静态资源复制失败: {e}")
    
    def _create_default_templates(self):
        """创建默认模板文件（如果不存在）"""
        default_templates = {
            'base.html': self._get_base_template(),
            'academic.html': self._get_academic_template(),
            'minimal.html': self._get_minimal_template(),
            'archive.html': self._get_archive_template(),
            'header.html': self._get_header_template(),
            'footer.html': self._get_footer_template()
        }
        
        for template_name, template_content in default_templates.items():
            template_path = self.template_dir / template_name
            if not template_path.exists():
                try:
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(template_content)
                except Exception as e:
                    print(f"⚠️ 创建模板失败 {template_name}: {e}")
    
    def _create_default_static_resources(self):
        """创建默认静态资源"""
        css_dir = self.static_dir / "css"
        css_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建CSS文件
        css_content = """/* RemUp默认样式 - 完整版 */
:root {
    /* 主色调 */
    --remup-primary: #3498db;
    --remup-secondary: #2ecc71;
    --remup-accent: #e74c3c;
    --remup-gray: #95a5a6;
    --remup-light-gray: #ecf0f1;
    
    /* 卡片颜色 */
    --card-bg: #ffffff;
    --card-shadow: rgba(0, 0, 0, 0.1);
    --card-border: #e0e0e0;
    
    /* 区域线颜色 */
    --region-line: #bdc3c7;
    --region-title: #7f8c8d;
    
    /* 字体 */
    --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
    --font-mono: 'Consolas', 'Monaco', 'Courier New', monospace;
}

/* 重置和基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-main);
    line-height: 1.6;
    color: #2c3e50;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
    min-height: 100vh;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
}

/* 页面标题样式 */
.page-header {
    text-align: center;
    margin-bottom: 40px;
    padding: 30px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
    color: var(--remup-primary);
    margin-bottom: 10px;
    font-size: 2.5em;
}

.page-header p {
    color: #7f8c8d;
    max-width: 600px;
    margin: 0 auto;
}

/* 主卡样式 */
.card {
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 4px 20px var(--card-shadow);
    border: 1px solid var(--card-border);
    padding: 24px;
    margin-bottom: 30px;
    position: relative;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
}

/* 卡片主题（标题） */
.card h2 {
    color: var(--remup-primary);
    border-bottom: 2px solid var(--remup-primary);
    padding-bottom: 12px;
    margin-bottom: 20px;
    font-size: 1.8em;
    position: relative;
    padding-left: 15px;
}

.card h2::before {
    content: '<+';
    color: var(--remup-gray);
    font-family: var(--font-mono);
    font-size: 0.8em;
    margin-right: 8px;
    opacity: 0.7;
}

.card h2::after {
    content: '/+>';
    color: var(--remup-gray);
    font-family: var(--font-mono);
    font-size: 0.8em;
    margin-left: 8px;
    opacity: 0.7;
}

/* 标签系统 */
.labels-container {
    position: absolute;
    top: 20px;
    right: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
    max-width: 300px;
}

.label {
    display: inline-flex;
    align-items: center;
    background: #f8f9fa;
    border-radius: 20px;
    padding: 6px 12px;
    text-decoration: none;
    color: #495057;
    font-size: 0.85em;
    transition: all 0.3s ease;
    max-width: 200px;
    overflow: hidden;
    border: 1px solid #dee2e6;
}

.label:hover {
    background: #e9ecef;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.label-symbol {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid var(--remup-primary);
    margin-right: 8px;
    font-size: 0.9em;
    font-weight: bold;
    color: var(--remup-primary);
    flex-shrink: 0;
}

.label-content {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}

/* 标签类型颜色 */
.label.important .label-symbol {
    border-color: var(--remup-accent);
    color: var(--remup-accent);
}

.label.success .label-symbol {
    border-color: #27ae60;
    color: #27ae60;
}

.label.warning .label-symbol {
    border-color: #f39c12;
    color: #f39c12;
}

.label.info .label-symbol {
    border-color: var(--remup-gray);
    color: var(--remup-gray);
}

/* 区域系统 */
.region {
    margin: 25px 0;
    position: relative;
}

.region-line {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        var(--region-line) 20%, 
        var(--region-line) 80%, 
        transparent 100%);
    margin: 10px 0 20px 0;
    position: relative;
}

.region-title {
    position: absolute;
    top: -10px;
    left: 10px;
    background: var(--card-bg);
    padding: 0 10px;
    font-size: 0.85em;
    font-weight: bold;
    color: var(--region-title);
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.region-content {
    margin-top: 15px;
}

/* 内容样式 */
.content {
    line-height: 1.8;
}

.content p {
    margin-bottom: 15px;
}

.content ul, .content ol {
    margin-left: 25px;
    margin-bottom: 15px;
}

.content li {
    margin-bottom: 8px;
    position: relative;
}

.content li::before {
    content: '•';
    color: var(--remup-primary);
    font-weight: bold;
    position: absolute;
    left: -15px;
}

/* 行内解释 */
.inline-explanation {
    display: block;
    color: #7f8c8d;
    opacity: 0.7;
    font-size: 0.9em;
    font-style: italic;
    margin-top: -5px;
    margin-bottom: 15px;
    padding-left: 20px;
    position: relative;
}

.inline-explanation::before {
    content: '>>';
    position: absolute;
    left: 0;
    color: var(--remup-gray);
    font-family: var(--font-mono);
}

/* 注卡系统 */
.annotation-container {
    position: relative;
    display: inline;
}

.annotation {
    cursor: help;
    border-bottom: 1px dashed var(--remup-primary);
    color: var(--remup-primary);
    padding: 2px 4px;
    border-radius: 3px;
    background: rgba(52, 152, 219, 0.1);
    transition: all 0.2s ease;
}

.annotation:hover {
    background: rgba(52, 152, 219, 0.2);
    border-bottom-style: solid;
}

.annotation-popup {
    display: none;
    position: absolute;
    z-index: 10000;
    background: white;
    border: 1px solid #bdc3c7;
    border-radius: 8px;
    padding: 12px;
    width: 250px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    font-size: 0.9em;
    line-height: 1.5;
    animation: fadeIn 0.2s ease;
    pointer-events: none;
}

.annotation-container:hover .annotation-popup {
    display: block;
    pointer-events: auto;
}

.annotation-popup.bottom {
    top: 100%;
    margin-top: 5px;
}

.annotation-popup.fixed {
    position: fixed !important;
    z-index: 10000;
}

/* 动画效果 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 代码块样式 */
.code-block {
    background: #2d3748;
    color: #e2e8f0;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 0.9em;
    line-height: 1.5;
    position: relative;
    z-index: 1;
}

.code-block pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* 代码高亮样式 */
.keyword { color: #c678dd; font-weight: bold; }
.number { color: #d19a66; }
.string { color: #98c379; }
.comment { color: #5c6370; font-style: italic; }

/* 归档系统 */
.archive {
    margin: 40px 0;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;
    position: relative;
}

.archive-title {
    font-size: 1.5em;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
}

.archive-title::before {
    content: '--<';
    font-family: var(--font-mono);
    margin-right: 8px;
    opacity: 0.8;
}

.archive-title::after {
    content: '>--';
    font-family: var(--font-mono);
    margin-left: 8px;
    opacity: 0.8;
}

.archive-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
    margin-top: 15px;
}

.archive-card-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    padding: 12px 20px;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 500;
    font-size: 0.95em;
    line-height: 1.4;
    box-shadow: 
        0 2px 8px rgba(102, 126, 234, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
}

/* 流光效果 */
.archive-card-link::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.2),
        transparent
    );
    transition: left 0.8s ease;
}

.archive-card-link:hover::before {
    left: 100%;
}

.archive-card-link:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 
        0 6px 20px rgba(102, 126, 234, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    text-decoration: none;
}

.archive-card {
    display: block;
    background: rgba(255, 255, 255, 0.1);
    padding: 10px;
    border-radius: 6px;
    text-decoration: none;
    color: white;
    transition: all 0.2s ease;
    text-align: center;
}

.archive-card:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

/* 增强交互样式 */
.card.enhanced-hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    z-index: 10;
}

.card.focused {
    outline: 2px solid var(--remup-primary);
    outline-offset: 2px;
    background: #f8f9fa;
}

.archive-nav-link.active {
    background: var(--remup-accent);
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .card {
        padding: 18px;
    }
    
    .labels-container {
        position: relative;
        top: 0;
        right: 0;
        margin-bottom: 15px;
        justify-content: flex-start;
        max-width: 100%;
    }
    
    .card h2 {
        font-size: 1.5em;
    }
    
    .archive-cards {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
}

@media (max-width: 600px) {
    .labels-container {
        position: relative !important;
        top: auto !important;
        right: auto !important;
        margin-bottom: 15px !important;
        justify-content: flex-start !important;
        max-width: 100% !important;
    }
}

@media (max-width: 480px) {
    .card {
        padding: 15px;
        border-radius: 8px;
    }
    
    .card h2 {
        font-size: 1.3em;
    }
    
    .label {
        font-size: 0.8em;
        padding: 5px 10px;
        max-width: 150px;
    }
    
    .label-symbol {
        width: 20px;
        height: 20px;
        font-size: 0.8em;
    }
    
    .annotation-popup {
        width: 200px;
        font-size: 0.85em;
    }
}

/* 工具类 */
.text-center { text-align: center; }
.text-right { text-align: right; }
.mt-1 { margin-top: 10px; }
.mb-1 { margin-bottom: 10px; }
.mt-2 { margin-top: 20px; }
.mb-2 { margin-bottom: 20px; }

/* 滚动锚点偏移 */
:target {
    scroll-margin-top: 20px;
}

/* 辅助功能优化 */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* 焦点样式 */
.card:focus {
    outline: 2px solid var(--remup-primary);
    outline-offset: 2px;
}

/* 加载状态 */
.loading {
    opacity: 0.7;
    pointer-events: none;
}

.loading::after {
    content: '加载中...';
    display: block;
    text-align: center;
    color: var(--remup-gray);
    font-style: italic;
}

/* 打印优化 */
@media print {
    .card {
        break-inside: avoid;
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        margin-bottom: 20px !important;
    }
    
    .annotation-popup {
        display: block !important;
        position: static !important;
        opacity: 1 !important;
        border: 1px solid #999 !important;
        margin: 5px 0 !important;
    }
    
    .page-header, .compile-info, .archives-nav {
        display: none !important;
    }
}"""
        
        css_file = css_dir / "remup.css"
        if not css_file.exists():
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
    
    def _get_base_template(self) -> str:
        """获取基础模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} - RemUp</title>
    <link rel="stylesheet" href="static/css/remup.css">
    <style>
        /* 内联关键样式 */
        .compile-info {
            text-align: center;
            color: #7f8c8d;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        .vibe-popup {
            display: none;
            position: absolute;
            background: white;
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            padding: 12px;
            max-width: 300px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            z-index: 1000;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 页面头部 -->
        <header class="page-header">
            <h1>{{ page_title }}</h1>
            <p>RemUp编译器生成的智能学习笔记</p>
            <div class="compile-info">
                <p>📅 编译时间: {{ compile_time }} | 📊 卡片总数: {{ total_all_cards }}</p>
            </div>
        </header>
        
        <!-- 主内容区域 -->
        <main class="main-content">
            {% for archive in archives %}
            <!-- 归档区域 -->
            <section class="archive" id="archive-{{ archive.id }}">
                <h2 class="archive-title">
                    <span class="archive-start">--&lt;</span>
                    {{ archive.name }}
                    <span class="archive-end">&gt;--</span>
                </h2>
                <span class="archive-count">({{ archive.card_count }} 张卡片)</span>
                
                <!-- 归档内卡片导航 -->
                <div class="archive-cards">
                    {% for card in archive.cards %}
                    <a href="#card-{{ card.id }}" class="archive-card-link">
                        {{ card.theme }}
                    </a>
                    {% endfor %}
                </div>
                
                <!-- 卡片内容 -->
                <div class="cards-container">
                    {% for card in archive.cards %}
                    <article class="card" id="card-{{ card.id }}">
                        <!-- 卡片标题 -->
                        <h3 class="card-title">
                            <span class="card-start-symbol">&lt;+</span>
                            {{ card.theme }}
                            <span class="card-end-symbol">/+&gt;</span>
                        </h3>
                        
                        <!-- 标签区域 -->
                        {% if card.labels %}
                        <div class="labels-container">
                            {% for label in card.labels %}
                            <div class="label {{ label.type }}">
                                <span class="label-symbol">{{ label.symbol }}</span>
                                <span class="label-content">
                                    {% for item in label.content %}
                                        {% if item.startswith('#') %}
                                        <a href="#card-{{ item[1:] | slugify }}" class="label-link">{{ item[1:] }}</a>
                                        {% else %}
                                        <span class="label-text">{{ item }}</span>
                                        {% endif %}
                                        {% if not loop.last %}, {% endif %}
                                    {% endfor %}
                                </span>
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}
                        
                        <!-- 区域内容 -->
                        {% for region in card.regions %}
                        <div class="region">
                            <hr class="region-line">
                            <div class="region-title">{{ region.name }}</div>
                            <div class="region-content">
                                <div class="content">{{ region.content | safe }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </article>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
            
            <!-- 注卡归档 -->
            {% if has_vibe_archive %}
            <section class="archive vibe-archive" id="vibe-archive">
                <h2 class="archive-title">
                    <span class="archive-start">--&lt;</span>
                    自动生成注卡
                    <span class="archive-end">&gt;--</span>
                </h2>
                <span class="archive-count">({{ total_vibe_cards }} 张注卡)</span>
                
                <div class="cards-container">
                    {% for card in vibe_archive.cards %}
                    <article class="card vibe-generated-card" id="vibe-card-{{ card.id }}">
                        <h3 class="card-title">
                            <span class="card-start-symbol">&lt;+</span>
                            {{ card.theme }}
                            <span class="card-end-symbol">/+&gt;</span>
                        </h3>
                        
                        {% for region in card.regions %}
                        <div class="region">
                            <hr class="region-line">
                            <div class="region-title">{{ region.name }}</div>
                            <div class="region-content">
                                <div class="content">{{ region.content | safe }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </article>
                    {% endfor %}
                </div>
            </section>
            {% endif %}
        </main>
    </div>

    <script>
        // 交互功能脚本
        document.addEventListener('DOMContentLoaded', function() {
            // 平滑滚动到锚点
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    if (targetId === '#') return;
                    
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        const yOffset = -20;
                        const y = targetElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
                        
                        window.scrollTo({
                            top: y,
                            behavior: 'smooth'
                        });
                    }
                });
            });
            
            // 注卡交互功能
            function setupVibeCards() {
                const annotationContainers = document.querySelectorAll('.annotation-container');
                
                annotationContainers.forEach(container => {
                    const annotation = container.querySelector('.annotation');
                    const popup = container.querySelector('.annotation-popup');
                    
                    if (!annotation || !popup) return;
                    
                    // 鼠标悬停显示注卡
                    annotation.addEventListener('mouseenter', function(e) {
                        const rect = annotation.getBoundingClientRect();
                        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                        
                        popup.classList.add('bottom');
                        popup.style.top = (rect.bottom + scrollTop + 5) + 'px';
                        popup.style.left = (rect.left + scrollLeft) + 'px';
                        
                        popup.style.display = 'block';
                    });
                    
                    annotation.addEventListener('mouseleave', function() {
                        popup.style.display = 'none';
                    });
                    
                    // 点击固定注卡
                    let isFixed = false;
                    annotation.addEventListener('click', function(e) {
                        e.stopPropagation();
                        isFixed = !isFixed;
                        
                        if (isFixed) {
                            popup.style.position = 'fixed';
                            popup.style.zIndex = '10000';
                            popup.classList.add('fixed');
                        } else {
                            popup.style.position = 'absolute';
                            popup.classList.remove('fixed');
                        }
                    });
                });
                
                // 点击页面其他位置关闭固定的注卡
                document.addEventListener('click', function() {
                    document.querySelectorAll('.annotation-popup.fixed').forEach(popup => {
                        popup.style.display = 'none';
                        popup.classList.remove('fixed');
                    });
                });
            }
            
            // 初始化注卡功能
            setupVibeCards();
            
            // 响应式标签容器调整
            function adjustLabelsContainer() {
                const cards = document.querySelectorAll('.card');
                
                cards.forEach(card => {
                    const labelsContainer = card.querySelector('.labels-container');
                    const cardTitle = card.querySelector('h3');
                    
                    if (!labelsContainer || !cardTitle) return;
                    
                    const cardWidth = card.offsetWidth;
                    if (cardWidth < 600) {
                        labelsContainer.style.position = 'relative';
                        labelsContainer.style.top = 'auto';
                        labelsContainer.style.right = 'auto';
                        labelsContainer.style.marginBottom = '15px';
                        labelsContainer.style.justifyContent = 'flex-start';
                        labelsContainer.style.maxWidth = '100%';
                    } else {
                        labelsContainer.style.position = 'absolute';
                        labelsContainer.style.top = '20px';
                        labelsContainer.style.right = '20px';
                        labelsContainer.style.justifyContent = 'flex-end';
                        labelsContainer.style.maxWidth = '300px';
                    }
                });
            }
            
            // 初始调整
            adjustLabelsContainer();
            window.addEventListener('resize', adjustLabelsContainer);
            
            console.log('RemUp页面初始化完成！');
        });
    </script>
</body>
</html>"""

    def _get_academic_template(self) -> str:
        """获取学术模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} - RemUp学术版</title>
    <link rel="stylesheet" href="static/css/remup.css">
    <style>
        /* 学术样式增强 */
        body {
            font-family: 'Times New Roman', serif;
            background: #fefefe;
        }
        .card {
            border-left: 4px solid #8B0000;
        }
        .card h3 {
            color: #8B0000;
            border-bottom: 1px solid #8B0000;
        }
        .citation {
            font-style: italic;
            color: #555;
            border-left: 3px solid #ccc;
            padding-left: 15px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="page-header" style="text-align: center; border-bottom: 2px solid #8B0000;">
            <h1 style="color: #8B0000;">{{ page_title }}</h1>
            <p>RemUp学术版 - 严谨的知识整理</p>
            <div class="compile-info">
                <p>生成于 {{ compile_time }} | 共 {{ total_all_cards }} 个知识点</p>
            </div>
        </header>
        
        <main class="main-content">
            {% for archive in archives %}
            <section class="archive">
                <h2>{{ archive.name }}</h2>
                {% for card in archive.cards %}
                <article class="card">
                    <h3>{{ card.theme }}</h3>
                    {% for region in card.regions %}
                    <div class="region">
                        <hr class="region-line">
                        <h4>{{ region.name }}</h4>
                        <div class="region-content">{{ region.content | safe }}</div>
                    </div>
                    {% endfor %}
                </article>
                {% endfor %}
            </section>
            {% endfor %}
        </main>
    </div>
</body>
</html>"""

    def _get_minimal_template(self) -> str:
        """获取简约模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background: white;
        }
        .card {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 20px;
            margin: 20px 0;
        }
        .card h3 {
            margin-top: 0;
            color: #007bff;
        }
        .region {
            margin: 15px 0;
        }
        .region h4 {
            color: #666;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
    </style>
</head>
<body>
    <header>
        <h1>{{ page_title }}</h1>
        {% if compile_time %}
        <p><small>生成于 {{ compile_time }}</small></p>
        {% endif %}
    </header>
    
    <main>
        {% for archive in archives %}
        <section>
            <h2>{{ archive.name }}</h2>
            {% for card in archive.cards %}
            <article class="card">
                <h3>{{ card.theme }}</h3>
                {% for region in card.regions %}
                <div class="region">
                    <h4>{{ region.name }}</h4>
                    <div>{{ region.content | safe }}</div>
                </div>
                {% endfor %}
            </article>
            {% endfor %}
        </section>
        {% endfor %}
    </main>
</body>
</html>"""

    def _get_archive_template(self) -> str:
        """获取归档模板"""
        return self._get_base_template()  # 使用基础模板

    def _get_header_template(self) -> str:
        """获取页头模板"""
        return """<header class="page-header">
    <h1>{{ page_title }}</h1>
    <p>RemUp编译器生成的智能学习笔记</p>
    <div class="compile-info">
        <p>📅 编译时间: {{ compile_time }} | 📊 卡片总数: {{ total_all_cards }}</p>
    </div>
</header>"""

    def _get_footer_template(self) -> str:
        """获取页脚模板"""
        return """<footer class="page-footer">
    <p>✨ Generated by <a href="https://github.com/yourusername/remup">RemUp Compiler</a> v{{ version }}</p>
</footer>"""


# 简化版本 - 向后兼容
class SimpleHTMLGenerator(HTMLGenerator):
    """简化版HTML生成器 - 向后兼容"""
    
    def generate(self, document_ast, output_file: Path, title: str) -> Path:
        """简化版生成方法"""
        return super().generate(document_ast, output_file, title, "default")


# 在文件末尾添加以下代码来定义缺失的类
class MockDocument:
    """用于测试的模拟文档类"""
    def __init__(self, archives):
        self.archives = archives
        self.vibe_archive = None

class MockArchive:
    """用于测试的模拟归档类"""
    def __init__(self, name, cards):
        self.name = name
        self.cards = cards

class MockCard:
    """用于测试的模拟卡片类"""
    def __init__(self, theme, labels=None, regions=None):
        self.theme = theme
        self.labels = labels or []
        self.regions = regions or []

class MockLabel:
    """用于测试的模拟标签类"""
    def __init__(self, symbol, content, label_type="default"):
        self.symbol = symbol
        self.content = content
        self.type = label_type

class MockRegion:
    """用于测试的模拟区域类"""
    def __init__(self, name, content, lines=None):
        self.name = name
        self.content = content
        self.lines = lines or []

# 测试代码 - 只有在直接运行此文件时才执行
# if __name__ == "__main__":
#     # 创建测试数据
#     test_region = MockRegion("内容", "这是一个`测试注卡`[这是一个测试注卡]的内容")
#     test_card = MockCard("测试卡片", 
#                         [MockLabel("!", ["重要"]), MockLabel(">", ["#相关卡片", "示例"])],
#                         [test_region])
#     test_archive = MockArchive("测试归档", [test_card])
#     test_document = MockDocument([test_archive])
    
#     # 测试HTML生成器
#     generator = HTMLGenerator()
    
#     try:
#         output_path = generator.generate(
#             test_document, 
#             Path("test_output.html"), 
#             "测试文档",
#             "default"
#         )
#         print(f"✅ HTML生成测试成功: {output_path}")
#     except Exception as e:
#         print(f"❌ HTML生成测试失败: {e}")
#         import traceback
#         traceback.print_exc()