#!/usr/bin/env python3
"""
HTML生成器 v3.1 - 修复label_types初始化问题
"""

import os
import re
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from remup.ast_nodes import *

class HTMLGenerator:
    """HTML生成器 - 支持外部CSS和多主题"""
    
    def __init__(self, project_root: str = None):
        """
        初始化HTML生成器
        
        Args:
            project_root: 项目根目录，用于查找static/css目录
        """
        # 首先初始化所有属性，避免任何可能的未初始化错误
        self.vibe_card_counter = 1
        self.current_card_theme = ""
        self.card_themes = set()
        self.vibe_cards_info = []
        
        # 标签类型映射 - 必须首先初始化
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
        
        # 然后进行项目根目录检测
        self.project_root = self._detect_project_root(project_root)
        self.static_css_dir = self.project_root / "static" / "css"
        self.available_themes = self._discover_available_themes()
        
        print(f"📁 项目根目录: {self.project_root}")
        print(f"🎨 静态CSS目录: {self.static_css_dir}")
        print(f"📋 发现 {len(self.available_themes)} 个可用主题: {list(self.available_themes.keys())}")
    
    def _detect_project_root(self, project_root: str = None) -> Path:
        """
        检测项目根目录（包含static/css的目录）
        
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
            # 1. 当前工作目录（可能是项目根目录）
            Path.cwd(),
            # 2. 脚本文件所在目录的父目录（HTML生成器在remup包内）
            Path(__file__).parent.parent,
            # 3. 环境变量指定的目录
            Path(os.environ.get('REMUP_PROJECT_ROOT', '')),
        ]
        
        # 添加一些常见的项目结构路径
        # 如果当前在子目录中，尝试向上查找
        current = Path.cwd()
        for _ in range(3):  # 最多向上查找3级
            if (current / "static" / "css").exists():
                possible_roots.append(current)
            current = current.parent
        
        # 检查可能的根目录
        for root in possible_roots:
            if root.exists():
                css_dir = root / "static" / "css"
                if css_dir.exists():
                    print(f"✅ 检测到项目根目录: {root}")
                    return root
                else:
                    print(f"❌ 目录存在但无static/css: {root}")
        
        # 如果都没找到，使用回退方案
        fallback_root = Path.cwd()
        print(f"⚠️ 未检测到标准项目结构，使用回退目录: {fallback_root}")
        return fallback_root
    
    def _discover_available_themes(self) -> Dict[str, Path]:
        """发现可用的CSS主题文件"""
        themes = {}
        
        # 检查static/css目录是否存在
        if not self.static_css_dir.exists():
            print(f"❌ CSS目录不存在: {self.static_css_dir}")
            return themes
        
        # 扫描CSS文件
        css_files = list(self.static_css_dir.glob("*.css"))
        if not css_files:
            print(f"⚠️ 在 {self.static_css_dir} 中未找到CSS文件")
            return themes
            
        for css_file in css_files:
            theme_name = css_file.stem
            themes[theme_name] = css_file
            print(f"✅ 发现主题: {theme_name}")
            
        return themes
    
    def get_available_themes(self) -> List[str]:
        """获取可用主题列表"""
        return list(self.available_themes.keys())
    
    def generate(self, document: Document, output_path: str, 
                 theme: str = "RemStyle", page_title: str = None) -> str:
        """
        生成完整的HTML文档
        
        Args:
            document: 文档AST
            output_path: 输出HTML文件路径
            theme: 主题名称（对应static/css下的CSS文件名，不含扩展名）
            page_title: 自定义页面标题
        """
        # 重置状态
        self.vibe_card_counter = 1
        self.vibe_cards_info = []
        self.card_themes = set()
        
        # 处理输出路径
        output_path = Path(output_path)
        self.output_dir = output_path.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"HTML生成器: 输出路径={output_path}, 主题={theme}")
        
        # 验证主题是否存在
        if theme not in self.available_themes:
            available = self.get_available_themes()
            if not available:
                raise ValueError(f"没有可用的CSS主题文件，请在 {self.static_css_dir} 中添加CSS文件")
            else:
                raise ValueError(f"主题 '{theme}' 不存在。可用主题: {', '.join(available)}")
        
        # 生成页面标题
        html_title = self._generate_page_title(document.title, page_title)
        print(f"页面标题: {html_title}")
        
        # 复制CSS文件到输出目录
        css_filename = self._copy_theme_css(theme, output_path.parent)
        
        # 收集所有卡片主题
        self._collect_card_themes(document)
        
        # 生成主卡内容
        main_content = self._generate_main_content(document.archives)
        
        # 生成注卡归档内容
        vibe_archive_content = self._generate_vibe_archive(document.vibe_archive)
        
        # 生成其他归档导航
        other_archives_content = self._generate_other_archives(document.archives)
        
        # 生成主题选择器
        theme_selector = self._generate_theme_selector(theme)
        
        # 构建完整HTML
        html_content = self._build_full_html(
            html_title,
            main_content,
            vibe_archive_content,
            other_archives_content,
            css_filename,
            theme_selector
        )
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML生成完成: {output_path} (主题: {theme})")
        return str(output_path)
    
    def _copy_theme_css(self, theme: str, output_dir: Path) -> str:
        """复制主题CSS文件到输出目录"""
        if theme not in self.available_themes:
            raise ValueError(f"主题 '{theme}' 不存在")
        
        source_css = self.available_themes[theme]
        target_css = output_dir / f"{theme}.css"
        
        try:
            shutil.copy2(source_css, target_css)
            print(f"CSS文件已复制: {source_css.name} -> {target_css}")
            return f"{theme}.css"
        except Exception as e:
            raise ValueError(f"无法复制CSS文件 {source_css}: {e}")
    
    def _generate_theme_selector(self, current_theme: str) -> str:
        """生成主题选择器HTML"""
        if len(self.available_themes) <= 1:
            return ""  # 只有一个主题时不显示选择器
        
        options = []
        for theme_name in sorted(self.available_themes.keys()):
            selected = "selected" if theme_name == current_theme else ""
            options.append(f'<option value="{theme_name}" {selected}>{theme_name}</option>')
        
        return f'''
        <div class="theme-selector-container">
            <label for="themeSelector">主题选择:</label>
            <select id="themeSelector" onchange="changeTheme(this.value)">
                {''.join(options)}
            </select>
        </div>
        '''
    
    def _generate_page_title(self, doc_title: str, custom_title: str = None) -> str:
        """生成页面标题"""
        if custom_title:
            return custom_title
        
        # 从文档标题中提取纯净文件名
        title = self._extract_clean_title(doc_title)
        return f"{title} - RemUp笔记"
    
    def _extract_clean_title(self, title: str) -> str:
        """从文档标题中提取纯净的文件名"""
        # 移除常见的文件扩展名
        extensions = ['.remup', '.ru', '.html', '.htm']
        for ext in extensions:
            if title.endswith(ext):
                title = title[:-len(ext)]
        
        # 如果是完整路径，只取文件名
        if '/' in title or '\\' in title:
            if '/' in title:
                parts = title.split('/')
            else:
                parts = title.split('\\')
            title = parts[-1]
        
        # 美化标题
        title = title.replace('_', ' ').strip()
        if title:
            title = ' '.join(word.capitalize() for word in title.split())
        
        return title if title else "RemUp笔记"
    
    def _collect_card_themes(self, document: Document):
        """收集所有卡片主题，用于跳转验证"""
        for archive in document.archives:
            for card in archive.cards:
                self.card_themes.add(card.theme)
    
    def _build_full_html(self, title: str, main_content: str, 
                        vibe_archive_content: str, other_archives_content: str,
                        css_filename: str, theme_selector: str) -> str:
        """构建完整的HTML文档结构"""
        
        safe_title = title.replace('"', '&quot;').replace("'", '&#39;')
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title}</title>
    <link rel="stylesheet" href="{css_filename}" id="mainStylesheet">
</head>
<body>
    <div class="container">
        <!-- 主题选择器 -->
        {theme_selector}
        
        <!-- 页面标题 -->
        <header class="page-header">
            <h1 class="page-title">{safe_title}</h1>
        </header>
        
        <!-- 主卡内容 -->
        <main class="main-content">
            {main_content}
        </main>
        
        <!-- 注卡归档 -->
        {vibe_archive_content}
        
        <!-- 其他归档 -->
        <nav class="other-archives">
            {other_archives_content}
        </nav>
    </div>
    
    <script>
        // 主题切换功能
        function changeTheme(themeName) {{
            const stylesheet = document.getElementById('mainStylesheet');
            stylesheet.href = themeName + '.css';
            
            // 保存用户选择到本地存储
            localStorage.setItem('preferredTheme', themeName);
        }}
        
        // 页面加载时应用保存的主题
        document.addEventListener('DOMContentLoaded', function() {{
            const savedTheme = localStorage.getItem('preferredTheme');
            if (savedTheme) {{
                const selector = document.getElementById('themeSelector');
                if (selector) {{
                    selector.value = savedTheme;
                    changeTheme(savedTheme);
                }}
            }}
        }});
        
        // 原有的交互功能
        document.addEventListener('DOMContentLoaded', function() {{
            // 1. 标签跳转功能
            const labelLinks = document.querySelectorAll('.label-link');
            labelLinks.forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ 
                            behavior: 'smooth', 
                            block: 'center' 
                        }});
                        
                        targetElement.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
                        setTimeout(() => {{
                            targetElement.style.backgroundColor = '';
                        }}, 2000);
                    }}
                }});
            }});

            // 2. 注卡跳转功能
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
                    annotations.forEach(annotation => {{
                        annotation.classList.remove('active');
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    # 其余方法保持不变...
    def _generate_main_content(self, archives: List[Archive]) -> str:
        """生成主卡内容"""
        content_parts = []
        for archive in archives:
            # 归档标题
            archive_html = f'''
            <section class="archive-section">
                <h2 class="archive-title">{archive.name}</h2>
                <div class="archive-cards">
            '''
            
            # 归档中的卡片
            for card in archive.cards:
                card_html = self._generate_card(card)
                archive_html += card_html
            
            archive_html += '''
                </div>
            </section>
            '''
            content_parts.append(archive_html)
        
        return '\n'.join(content_parts)
    
    def _normalize_id(self, theme: str) -> str:
        """将主题文本转换为安全的HTML ID"""
        # 将空格和特殊字符转换为连字符
        import re
        normalized = re.sub(r'[^\w\s-]', '', theme)  # 移除非字母数字字符
        normalized = re.sub(r'[-\s]+', '-', normalized)  # 将空格和连字符统一
        normalized = normalized.lower().strip('-')
        return f"card-{normalized}"  # 添加前缀避免纯数字ID

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
        
        # 使用标准化的ID
        card_id = self._normalize_id(card.theme)
        
        # 生成标签和区域内容...
        return f'''
        <div class="card" id="{card_id}">
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
                card_id = self._normalize_id(card.theme)
                card_links.append(f'<a href="#{card_id}" class="archive-card-link">{card.theme}</a>')
            
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
    

def print_generation_summary(document: Document, output_path: str, theme: str):
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
    print(f"🎨 使用主题: {theme}")
    print(f"📂 归档数量: {len(document.archives)}")
    print(f"🃏 卡片总数: {total_cards}")
    print(f"💡 注卡数量: {total_vibe_cards}")
    print(f"📋 注卡归档: {'✅ 有' if document.vibe_archive else '❌ 无'}")
    print("=" * 60)

# 使用示例
if __name__ == "__main__":
    # 创建HTML生成器实例
    generator = HTMLGenerator(project_root=".")
    
    # 获取可用主题
    themes = generator.get_available_themes()
    print(f"可用主题: {themes}")
    
    # 使用示例（需要实际的document对象）
    # result = generator.generate(document, "output.html", theme="RemStyle")