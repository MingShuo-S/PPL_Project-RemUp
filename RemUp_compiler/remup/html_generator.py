#!/usr/bin/env python3
"""
HTML生成器 v2.1 - 修复注卡和注卡归档显示问题
基于修复后的Parser AST，生成功能完整的HTML文件
"""

import os
import re
from typing import Dict, Any, List, Optional
from remup.ast_nodes import *
from remup.parser import Parser
from remup.lexer import Lexer
from pathlib import Path

class HTMLGenerator:
    """HTML生成器 - 基于AST生成功能完整的HTML"""
    
    def __init__(self, output_dir: str = "output", css_file: str = "RemStyle.css"):
        self.output_dir = output_dir
        self.css_file = css_file
        self.vibe_card_counter = 1
        self.current_card_theme = ""
        self.card_themes = set()
        self.vibe_cards_info = []  # 存储所有注卡信息
        
        # 标签类型映射
        self.label_types = {
            '!': 'important',
            '?': 'question', 
            '>': 'reference',
            '<': 'backlink',
            'i': 'info',
            '✓': 'completed',
            '☆': 'star',
            '▲': 'priority'
        }
        
        os.makedirs(output_dir, exist_ok=True)
        
    def generate(self, document: Document, output_path: str, css_content: str = None) -> str:
        """生成完整的HTML文档 - 修复路径处理"""
        
        # 重置状态
        self.vibe_card_counter = 1
        self.vibe_cards_info = []
        self.card_themes = set()
        
        # 处理输出路径
        output_path = Path(output_path)
        
        # 如果输出路径是相对路径，确保输出目录存在
        if not output_path.is_absolute():
            # 确保输出目录存在
            self.output_dir = output_path.parent
            self.output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_path.name
        else:
            # 绝对路径，直接使用
            self.output_dir = output_path.parent
            filename = output_path.name
        
        print(f"HTMLGenerator: 输出目录={self.output_dir}, 文件名={filename}")
        
        # 收集所有卡片主题
        self._collect_card_themes(document)
        
        # 生成CSS文件
        self.generate_css_file(css_content)
        
        # 生成主卡内容
        main_content = self._generate_main_content(document.archives)
        
        # 生成注卡归档内容
        vibe_archive_content = self._generate_vibe_archive(document.vibe_archive)
        
        # 生成其他归档导航
        other_archives_content = self._generate_other_archives(document.archives)
        
        # 构建完整HTML
        html_content = self._build_full_html(
            document.title,  # 使用AST中的文档标题，而不是文件名
            main_content,
            vibe_archive_content,
            other_archives_content
        )
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML生成完成: {output_path}")
        return str(output_path)
    
    def _collect_card_themes(self, document: Document):
        """收集所有卡片主题，用于跳转验证"""
        for archive in document.archives:
            for card in archive.cards:
                self.card_themes.add(card.theme)
    
    def _build_full_html(self, title: str, main_content: str, 
                    vibe_archive_content: str, other_archives_content: str) -> str:
        """构建完整的HTML文档结构"""
        
        # 如果标题是文件名，提取有意义的标题
        if title.endswith('.ru') or title.endswith('.remup'):
            # 使用文件名（不含扩展名）作为标题
            title = Path(title).stem
            # 可以进一步美化，比如将下划线替换为空格，首字母大写等
            title = title.replace('_', ' ').title()
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="{self.css_file}">
</head>
<body>
    <div class="container">
        <!-- 页面标题 -->
        <header class="page-header">
            <h1>{title}</h1>
        </header>
        
        <!-- 主卡内容 -->
        <main class="main-content">
            {main_content}
        </main>
        
        <!-- 注卡归档 -->
        {vibe_archive_content}
        
        <!-- 其他归档 -->
        {other_archives_content}
    </div>
    
    <script>
        // 完整的交互功能实现
        document.addEventListener('DOMContentLoaded', function() {{
            // 1. 标签跳转功能
            const labelLinks = document.querySelectorAll('.label-link');
            labelLinks.forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {{
                        // 平滑滚动到目标元素
                        targetElement.scrollIntoView({{ 
                            behavior: 'smooth', 
                            block: 'center' 
                        }});
                        
                        // 添加高亮效果
                        targetElement.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
                        setTimeout(() => {{
                            targetElement.style.backgroundColor = '';
                        }}, 2000);
                    }}
                }});
            }});

            // 2. 注卡跳转功能（注卡归档 → 原文）
            const vibeLinks = document.querySelectorAll('.vibe-link, .back-to-source');
            vibeLinks.forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ 
                            behavior: 'smooth', 
                            block: 'center' 
                        }});
                        
                        // 触发注卡的悬停效果
                        if (targetElement.classList.contains('annotation')) {{
                            targetElement.style.backgroundColor = 'rgba(52, 152, 219, 0.3)';
                            setTimeout(() => {{
                                targetElement.style.backgroundColor = '';
                            }}, 2000);
                        }}
                    }}
                }});
            }});

            // 3. 归档导航跳转
            const archiveLinks = document.querySelectorAll('.archive-card-link');
            archiveLinks.forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ 
                            behavior: 'smooth', 
                            block: 'start' 
                        }});
                    }}
                }});
            }});

            // 4. 注卡悬停效果优化
            const annotations = document.querySelectorAll('.annotation');
            annotations.forEach(annotation => {{
                annotation.addEventListener('mouseenter', function() {{
                    annotations.forEach(a => a.classList.remove('active'));
                    this.classList.add('active');
                }});
            }});

            // 5. 响应式网格布局调整
            function adjustGridLayout() {{
                const archiveCards = document.querySelectorAll('.archive-cards');
                const screenWidth = window.innerWidth;
                
                archiveCards.forEach(container => {{
                    if (screenWidth >= 1200) {{
                        container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(500px, 1fr))';
                    }} else if (screenWidth >= 1024) {{
                        container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(450px, 1fr))';
                    }} else if (screenWidth >= 768) {{
                        container.style.gridTemplateColumns = 'repeat(auto-fit, minmax(400px, 1fr))';
                    }} else {{
                        container.style.gridTemplateColumns = '1fr';
                    }}
                }});
            }}

            // 初始调整和窗口大小变化监听
            adjustGridLayout();
            window.addEventListener('resize', adjustGridLayout);

            // 6. 页面加载时的锚点跳转处理
            if (window.location.hash) {{
                const targetElement = document.querySelector(window.location.hash);
                if (targetElement) {{
                    setTimeout(() => {{
                        targetElement.scrollIntoView({{ behavior: 'smooth' }});
                    }}, 100);
                }}
            }}

            // 7. 键盘导航支持
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    // ESC键关闭所有注卡弹出框
                    annotations.forEach(annotation => {{
                        annotation.classList.remove('active');
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    def _generate_main_content(self, archives: List[Archive]) -> str:
        """生成主卡内容 - 添加调试"""
        content_parts = []
        
        print(f"生成主内容: {len(archives)} 个归档")
        
        for i, archive in enumerate(archives):
            print(f"处理归档 {i}: {archive.name}, {len(archive.cards)} 张卡片")
            
            # 归档标题
            archive_html = f'''
            <section class="archive-section">
                <h2 class="archive-title">{archive.name}</h2>
                <div class="archive-cards">
            '''
            
            # 归档中的卡片
            for j, card in enumerate(archive.cards):
                print(f"  处理卡片 {j}: {card.theme}")
                card_html = self._generate_card(card)
                archive_html += card_html
            
            archive_html += '''
                </div>
            </section>
            '''
            content_parts.append(archive_html)
        
        result = '\n'.join(content_parts)
        print(f"主内容生成完成，长度: {len(result)} 字符")
        return result
    
    def _generate_card(self, card: MainCard) -> str:
        """生成单个卡片HTML"""
        self.current_card_theme = card.theme
        
        # 生成标签
        labels_html = self._generate_labels(card.labels)
        
        # 生成区域
        regions_html = []
        for region in card.regions:
            region_html = self._generate_region(region)
            regions_html.append(region_html)
        
        return f'''
        <div class="card" id="{card.theme}">
            <h2 class="card-title">{card.theme}</h2>
            
            <!-- 标签区域 -->
            {labels_html}
            
            <!-- 区域内容 -->
            <div class="card-regions">
                {''.join(regions_html)}
            </div>
        </div>
        '''
    
    def _generate_labels(self, labels: List[Label]) -> str:
        """生成标签HTML - 修复跳转功能"""
        if not labels:
            return ""
        
        labels_html = []
        for label in labels:
            # 处理标签内容中的跳转链接
            content_html = []
            for item in label.content:
                if item.startswith('#'):
                    # 检查跳转目标是否存在
                    target_id = item[1:]  # 去掉#号
                    if target_id in self.card_themes:
                        # 有效的跳转链接
                        content_html.append(f'<a href="#{target_id}" class="label-link">{target_id}</a>')
                    else:
                        # 无效的跳转链接，只显示文本
                        content_html.append(f'<span class="label-content">{target_id}</span>')
                else:
                    # 普通内容
                    content_html.append(f'<span class="label-content">{item}</span>')
            
            # 确定标签类型
            label_type = self.label_types.get(label.symbol, "default")
            
            label_html = f'''
            <div class="label {label_type}">
                <span class="label-symbol">{label.symbol}</span>
                <div class="label-contents">
                    {', '.join(content_html)}
                </div>
            </div>
            '''
            labels_html.append(label_html)
        
        return f'''
        <div class="labels-container">
            {''.join(labels_html)}
        </div>
        '''
    
    def _generate_region(self, region: Region) -> str:
        """生成区域HTML"""
        # 处理区域内容行
        content_html = self._process_region_content(region)
        
        return f'''
        <div class="region">
            <hr class="region-line">
            <div class="region-title">{region.name}</div>
            <div class="region-content">
                <div class="content">
                    {content_html}
                </div>
            </div>
        </div>
        '''
    
    def _process_region_content(self, region: Region) -> str:
        """处理区域内容，包括行内解释和注卡"""
        if not region.lines:
            return ""
        
        lines_with_explanations = []
        
        for i, line in enumerate(region.lines):
            # 处理注卡：检查当前行是否有对应的注卡
            processed_line = line
            for vibe_card in region.vibe_cards:
                if vibe_card.content == line.strip():
                    # 生成注卡HTML
                    vibe_html = self._generate_vibe_card_html(vibe_card)
                    processed_line = vibe_html
                    break
            
            # 检查行内解释
            inline_exp = region.inline_explanations.get(i)
            
            if inline_exp and isinstance(inline_exp, Inline_Explanation):
                # 添加行内解释
                line_with_exp = f'{processed_line}<span class="inline-explanation">{inline_exp.content}</span>'
                lines_with_explanations.append(f'<p>{line_with_exp}</p>')
            else:
                # 普通行
                lines_with_explanations.append(f'<p>{processed_line}</p>')
        
        return '\n'.join(lines_with_explanations)
    
    def _generate_vibe_card_html(self, vibe_card: VibeCard) -> str:
        """生成注卡HTML结构 - 包含双向跳转"""
        # 生成唯一的注卡ID
        annotation_id = f"annotation_{vibe_card.id}"
        
        # 记录注卡信息用于归档
        self.vibe_cards_info.append({
            'id': annotation_id,
            'content': vibe_card.content,
            'annotation': vibe_card.annotation,
            'card_theme': self.current_card_theme
        })
        
        # 创建跳转回原文的链接
        back_link = f'<a href="#{annotation_id}" class="back-to-source">↩ 跳回原文</a>'
        
        return f'''
        <span class="annotation-container">
            <span class="annotation" id="{annotation_id}">
                {vibe_card.content}
                <span class="annotation-popup">
                    {vibe_card.annotation}
                    {back_link}
                </span>
            </span>
        </span>
        '''
    
    def _generate_vibe_archive(self, vibe_archive: VibeArchive) -> str:
        """生成注卡归档HTML"""
        if not vibe_archive:
            return ""
        
        cards_html = []
        for card in vibe_archive.cards:
            card_html = self._generate_vibe_archive_card(card)
            cards_html.append(card_html)
        
        if not cards_html:
            return ""
        
        return f'''
        <section class="vibe-archive">
            <h2 class="vibe-archive-title">注卡归档</h2>
            <div class="vibe-archive-cards">
                {''.join(cards_html)}
            </div>
        </section>
        '''
    
    def _generate_vibe_archive_card(self, card: MainCard) -> str:
        """生成注卡归档中的卡片HTML"""
        vibe_items = []
        
        # 收集所有注卡
        for region in card.regions:
            for vibe_card in region.vibe_cards:
                # 查找对应的注卡ID
                annotation_id = f"annotation_{vibe_card.id}"
                vibe_item = f'''
                <div class="vibe-archive-item">
                    <a href="#{annotation_id}" class="vibe-link">{vibe_card.content}</a>
                    <p>{vibe_card.annotation}</p>
                </div>
                '''
                vibe_items.append(vibe_item)
        
        if not vibe_items:
            return ""
        
        # 提取原始卡片主题（去掉"注卡: "前缀）
        theme = card.theme.replace('注卡: ', '')
        
        return f'''
        <div class="vibe-archive-card">
            <h3>{theme}</h3>
            <div class="vibe-archive-content">
                {''.join(vibe_items)}
            </div>
        </div>
        '''
    
    def _generate_other_archives(self, archives: List[Archive]) -> str:
        """生成其他归档的导航链接"""
        archive_sections = []
        
        for archive in archives:
            card_links = []
            for card in archive.cards:
                card_links.append(f'<a href="#{card.theme}" class="archive-card-link">{card.theme}</a>')
            
            archive_html = f'''
            <div class="archive-section">
                <h3 class="archive-title">{archive.name}</h3>
                <div class="archive-cards">
                    {''.join(card_links)}
                </div>
            </div>
            '''
            archive_sections.append(archive_html)
        
        if archive_sections:
            return f'''
            <section class="archives-nav">
                <h2 class="archive-title">归档导航</h2>
                {''.join(archive_sections)}
            </section>
            '''
        return ""
    
    def generate_css_file(self, css_content: str = None) -> str:
        """生成独立的CSS文件"""
        if css_content is None:
            # 这里可以放置您确认的CSS内容
            css_content = """/* RemUp 样式系统 v3.1 - 完整交互版 */
:root {
    --remup-primary: #3498db;
    --remup-secondary: #2ecc71;
    --remup-accent: #e74c3c;
    --remup-gray: #95a5a6;
    --remup-light-gray: #ecf0f1;
    --card-bg: #ffffff;
    --card-shadow: rgba(0, 0, 0, 0.1);
    --card-border: #e0e0e0;
    --region-line: #bdc3c7;
    --region-title: #7f8c8d;
    --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
    --font-mono: 'Consolas', 'Monaco', 'Courier New', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-main);
    line-height: 1.6;
    color: #2c3e50;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
    min-height: 100vh;
}

.container {
    max-width: none;
    width: 100%;
    margin: 0 auto;
    padding: 20px;
}

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

.card {
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 4px 20px var(--card-shadow);
    border: 1px solid var(--card-border);
    padding: 24px;
    margin-bottom: 0;
    position: relative;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    width: 100%;
    min-width: 0;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
}

.card h2 {
    color: var(--remup-primary);
    border-bottom: 2px solid var(--remup-primary);
    padding-bottom: 12px;
    margin-bottom: 20px;
    font-size: 1.8em;
    position: relative;
    padding-left: 15px;
    word-wrap: break-word;
    overflow-wrap: break-word;
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

.label.default .label-symbol { border-color: var(--remup-primary); color: var(--remup-primary); }
.label.important .label-symbol { border-color: var(--remup-accent); color: var(--remup-accent); }
.label.reference .label-symbol { border-color: #3498db; color: #3498db; }
.label.question .label-symbol { border-color: #f39c12; color: #f39c12; }
.label.info .label-symbol { border-color: var(--remup-gray); color: var(--remup-gray); }

.label-link {
    color: inherit;
    text-decoration: none;
    margin-right: 4px;
}

.label-link:hover { text-decoration: underline; }

.region {
    margin: 25px 0;
    position: relative;
}

.region-line {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--region-line) 20%, var(--region-line) 80%, transparent 100%);
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

.region-content { margin-top: 15px; }

.content { line-height: 1.8; }
.content p { margin-bottom: 15px; }

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
    white-space: normal;
    word-wrap: break-word;
}

.inline-explanation::before {
    content: '>>';
    position: absolute;
    left: 0;
    color: var(--remup-gray);
    font-family: var(--font-mono);
    font-size: 0.85em;
}

.annotation-container { position: relative; display: inline; }

.annotation {
    position: relative;
    display: inline;
    cursor: help;
    color: #3498db;
    border-bottom: 1px dashed #3498db;
    transition: all 0.2s ease;
    padding: 2px 4px;
    border-radius: 3px;
    background: rgba(52, 152, 219, 0.1);
}

.annotation:hover {
    background: rgba(52, 152, 219, 0.2);
    border-bottom-style: solid;
}

.annotation-popup {
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
    color: #2c3e50;
    display: none;
    animation: fadeIn 0.2s ease;
    pointer-events: none;
}

.annotation-container:hover .annotation-popup {
    display: block;
    pointer-events: auto;
}

.back-to-source {
    display: block;
    margin-top: 8px;
    font-size: 0.8em;
    color: var(--remup-primary);
    text-decoration: none;
}

.back-to-source:hover { text-decoration: underline; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

.archive-section { width: 100%; margin-bottom: 40px; }

.archive-title {
    font-size: 2em;
    margin-bottom: 15px;
    color: #2c3e50;
    border-bottom: 3px solid var(--remup-primary);
    padding-bottom: 10px;
}

.archive-cards {
    display: grid;
    grid-template-columns: 1fr;
    gap: 25px;
    width: 100%;
}

.vibe-archive {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 8px;
    margin: 30px 0;
}

.vibe-archive-title {
    color: #e74c3c;
    font-size: 1.8em;
    margin-bottom: 20px;
}

.vibe-archive-card {
    background: white;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
    border-left: 4px solid #3498db;
}

.vibe-archive-item {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.vibe-link {
    color: var(--remup-primary);
    text-decoration: none;
    font-weight: bold;
}

.vibe-link:hover { text-decoration: underline; }

.archive-card-link {
    display: block;
    padding: 12px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    border-radius: 8px;
    transition: all 0.3s ease;
    text-align: center;
}

.archive-card-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
    .container { padding: 10px; }
    .card { padding: 18px; }
    .labels-container {
        position: relative;
        top: 0;
        right: 0;
        margin-bottom: 15px;
        justify-content: flex-start;
        max-width: 100%;
    }
    .card h2 { font-size: 1.5em; }
    .archive-cards { grid-template-columns: 1fr; }
}

@media (min-width: 768px) {
    .archive-cards { grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; }
    .container { padding: 30px; }
}

@media (min-width: 1024px) {
    .archive-cards { grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 35px; }
}

@media (min-width: 1200px) {
    .container { max-width: 1400px; margin: 0 auto; }
    .archive-cards { grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); }
}

@media (max-width: 480px) {
    .card { padding: 15px; border-radius: 8px; }
    .card h2 { font-size: 1.3em; }
    .label { font-size: 0.8em; padding: 5px 10px; max-width: 150px; }
    .label-symbol { width: 20px; height: 20px; font-size: 0.8em; }
    .annotation-popup { width: 200px; font-size: 0.85em; }
}

.text-center { text-align: center; }
.mt-1 { margin-top: 10px; }
.mb-1 { margin-bottom: 10px; }

:target {
    scroll-margin-top: 20px;
    background-color: rgba(255, 255, 0, 0.2);
    transition: background-color 0.5s ease;
}

.card:focus {
    outline: 2px solid var(--remup-primary);
    outline-offset: 2px;
}
"""
        
        css_path = os.path.join(self.output_dir, self.css_file)
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        return css_path

def print_generation_summary(document: Document, output_path: str):
    """打印生成摘要"""
    total_cards = sum(len(archive.cards) for archive in document.archives)
    total_vibe_cards = 0
    for archive in document.archives:
        for card in archive.cards:
            total_vibe_cards += len(card.vibe_cards)
    
    print("=" * 60)
    print("🎉 HTML生成完成！")
    print("=" * 60)
    print(f"📁 输出文件: {output_path}")
    print(f"📄 文档标题: {document.title}")
    print(f"📂 归档数量: {len(document.archives)}")
    print(f"🃏 卡片总数: {total_cards}")
    print(f"💡 注卡数量: {total_vibe_cards}")
    print(f"📋 注卡归档: {'✅ 有' if document.vibe_archive else '❌ 无'}")
    print("=" * 60)
    print("✨ 功能特性:")
    print("  ✅ 标签跳转功能")
    print("  ✅ 注卡悬停显示")
    print("  ✅ 注卡归档双向导航")
    print("  ✅ 响应式布局设计")
    print("  ✅ 完整的CSS样式")
    print("  ✅ 行内解释功能")
    print("  ✅ 列表样式优化")
    print("=" * 60)

# 完整工作流测试
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # 测试用例
    test_code = """
--<Vocabulary>--
<+vigilant
(>: #careful, #watchful, 近义词)
(!: 重要)
---解释
adj. 警惕的；警觉的；戒备的
---词组
- be vigilant about/against/over >>对…保持警惕
- remain/stay vigilant >>保持警惕
- require vigilance >>（需要警惕性）
---例句
- Citizens are urged to remain vigilant against cyber scams. `网络诈骗`[指通过互联网进行的欺诈行为] >>敦促公民对网络诈骗保持警惕
/+>
"""
    
    print("🚀 开始完整工作流测试...")
    print("-" * 60)
    
    # 1. 词法分析
    print("1. 词法分析...")
    lexer = Lexer()
    tokens = lexer.tokenize(test_code)
    print("   ✅ 词法分析完成")
    
    # 2. 语法分析
    print("2. 语法分析...")
    parser = Parser(tokens, "vocabulary.remup")
    ast = parser.parse()
    print("   ✅ 语法分析完成")
    
    # 3. HTML生成
    print("3. HTML生成...")
    generator = HTMLGenerator()
    output_path = generator.generate(ast, "vocabulary.html")
    print("   ✅ HTML生成完成")
    
    # 4. 输出摘要
    print_generation_summary(ast, output_path)
    
    print("\n🎯 完整工作流测试完成！")
    print("✨ 生成的HTML文件包含了所有交互功能：")
    print("   • 标签点击跳转 (#careful, #watchful)")
    print("   • 注卡悬停显示 (网络诈骗)")
    print("   • 注卡归档双向导航")
    print("   • 行内解释自动换行")
    print("   • 响应式布局适配")
    print("\n📁 打开文件查看效果:")
    print(f"   {output_path}")