"""
RemUp语法解析器 v2.0 - 完整版
支持完整的RemUp语法，包括注卡、标签、区域、行内解释等
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from .ast_nodes import Document, Archive, MainCard, Label, Region, VibeCard, VibeArchive

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParseState:
    """解析状态机"""
    current_archive: Optional[Archive] = None
    current_card: Optional[MainCard] = None
    current_region: Optional[Region] = None
    line_number: int = 0
    indent_level: int = 0
    in_code_block: bool = False
    code_block_language: str = ""
    code_block_content: List[str] = None

class RemUpParser:
    """
    RemUp语法解析器 - 完整版
    
    支持的语法：
    1. 归档定义: --<归档名>--
    2. 卡片定义: <+主题 /+>
    3. 标签定义: (符号: 内容)
    4. 区域定义: ---区域名
    5. 注卡语法: `内容`[批注]
    6. 行内解释: >>解释文本
    7. 代码块: ```语言 ... ```
    8. 注释: # 注释内容
    """
    
    # 语法模式定义
    PATTERNS = {
        'archive': re.compile(r'^--<([^>]+)>--\s*$'),
        'card_start': re.compile(r'^<\+([^/]+)\s*$'),
        'card_end': re.compile(r'^/\+>\s*$'),
        'label': re.compile(r'^\(([^:]+):\s*([^)]+)\)\s*$'),
        'region': re.compile(r'^---\s*(\w+)\s*$'),
        'vibe_card': re.compile(r'`([^`]+)`\[([^\]]+)\]'),
        'inline_explanation': re.compile(r'>>\s*([^\n<]+)'),
        'comment': re.compile(r'^\s*#'),
        'code_block_start': re.compile(r'^```\s*(\w*)\s*$'),
        'code_block_end': re.compile(r'^```\s*$'),
        'empty_line': re.compile(r'^\s*$')
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.state = ParseState()
        self.vibe_processor = VibeCardProcessor()
        self.archives = []  # 存储所有归档的列表
    
    def parse(self, source: str) -> Document:
        """解析RemUp源代码 - 修复版"""
        if self.verbose:
            logger.info("开始解析RemUp源代码")
        
        # 重置解析状态
        self.state = ParseState()
        self.archives = []  # 重置归档列表
        
        lines = source.split('\n')
        
        try:
            i = 0
            while i < len(lines):
                self.state.line_number = i + 1
                line = lines[i].strip()
                
                if self.verbose:
                    logger.debug(f"行 {i+1}: {line[:50]}{'...' if len(line) > 50 else ''}")
                
                # 处理当前行
                processed = self._process_line(line, lines, i)
                if processed is not None:
                    i = processed  # 跳转到处理后的行号
                else:
                    i += 1
                
                # 安全检查，防止无限循环
                if i > len(lines) * 2:
                    raise RuntimeError("解析器可能进入无限循环")
            
            # 保存最后一个归档（如果存在且包含卡片）
            if (self.state.current_archive and 
                self.state.current_archive.cards and 
                self.state.current_archive not in self.archives):
                
                self.archives.append(self.state.current_archive)
                if self.verbose:
                    logger.info(f"完成归档: {self.state.current_archive.name} (包含{len(self.state.current_archive.cards)}张卡片)")
            
            # 如果没有归档但有卡片，创建默认归档
            if not self.archives and self.state.current_card:
                default_archive = Archive(name="默认归档", cards=[self.state.current_card])
                self.archives.append(default_archive)
                if self.verbose:
                    logger.info("创建默认归档")
            
            # 创建文档
            document = Document(archives=self.archives)
            
            # 处理注卡
            if self.verbose:
                logger.info("处理注卡系统")
            document = self.vibe_processor.process(document)
            
            if self.verbose:
                total_cards = sum(len(archive.cards) for archive in self.archives)
                logger.info(f"解析完成: {len(self.archives)}个归档, {total_cards}张卡片")
            
            return document
            
        except Exception as e:
            logger.error(f"解析错误 (行 {self.state.line_number}): {e}")
            if self.verbose:
                # 提供更多错误上下文
                start_line = max(0, self.state.line_number - 3)
                end_line = min(len(lines), self.state.line_number + 2)
                context = "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines[start_line:end_line], start_line))
                logger.error(f"错误上下文:\n{context}")
            raise
    
    def _process_archive_start(self, match: re.Match, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理归档开始 - 完整修复版"""
        archive_name = match.group(1).strip()
        
        # 保存之前的归档（如果存在且包含卡片）
        if (self.state.current_archive and 
            self.state.current_archive.cards and 
            self.state.current_archive not in self.archives):
            
            self.archives.append(self.state.current_archive)
            if self.verbose:
                logger.info(f"完成归档: {self.state.current_archive.name} (包含{len(self.state.current_archive.cards)}张卡片)")
        
        # 创建新归档
        self.state.current_archive = Archive(
            name=archive_name,
            cards=[],
            description=self._extract_archive_description(all_lines, current_index)
        )
        
        # 将新归档添加到列表
        if self.state.current_archive not in self.archives:
            self.archives.append(self.state.current_archive)
        
        # 重置当前卡片和区域状态
        self.state.current_card = None
        self.state.current_region = None
        
        if self.verbose:
            logger.info(f"开始归档: {archive_name}")
        
        return None
    
    def _extract_archive_description(self, all_lines: List[str], current_index: int) -> str:
        """提取归档描述（归档定义后的注释）"""
        description = ""
        next_line_index = current_index + 1
        
        # 最多查看接下来的5行注释
        max_lines = min(5, len(all_lines) - current_index - 1)
        
        for i in range(max_lines):
            line_index = current_index + i + 1
            if line_index >= len(all_lines):
                break
                
            line = all_lines[line_index].strip()
            
            # 如果是空行，继续查找
            if not line:
                continue
                
            # 如果是注释，提取内容
            if line.startswith('#'):
                comment_content = line[1:].strip()
                if description:
                    description += " " + comment_content
                else:
                    description = comment_content
            else:
                # 遇到非注释行，停止提取
                break
        
        return description
    
    def _process_card_start(self, match: re.Match, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理卡片开始 - 修复版"""
        theme = match.group(1).strip()
        
        # 确保有当前归档
        if not self.state.current_archive:
            # 创建默认归档
            self.state.current_archive = Archive(name="默认归档", cards=[])
            if self.state.current_archive not in self.archives:
                self.archives.append(self.state.current_archive)
            if self.verbose:
                logger.info("创建默认归档")
        
        # 创建新卡片
        self.state.current_card = MainCard(
            theme=theme,
            labels=[],
            regions=[],
            vibe_cards=[],
            metadata=self._extract_card_metadata(all_lines, current_index)
        )
        
        # 添加到当前归档
        self.state.current_archive.cards.append(self.state.current_card)
        
        # 重置当前区域
        self.state.current_region = None
        
        if self.verbose:
            logger.info(f"开始卡片: {theme}")
        
        return None
    
    def _process_card_end(self, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理卡片结束 - 修复版"""
        if self.state.current_card:
            if self.verbose:
                logger.info(f"结束卡片: {self.state.current_card.theme}")
            
            # 检查卡片是否有效（至少有一个区域）
            if not self.state.current_card.regions:
                logger.warning(f"卡片 '{self.state.current_card.theme}' 没有区域内容")
            
            self.state.current_card = None
            self.state.current_region = None
        
        return None
    
    def _process_region_start(self, match: re.Match, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理区域开始 - 修复版"""
        if not self.state.current_card:
            logger.warning(f"行 {self.state.line_number}: 区域定义必须在卡片内部")
            return None
        
        region_name = match.group(1).strip()
        
        # 创建新区域
        self.state.current_region = Region(
            name=region_name,
            content="",
            lines=[],
            vibe_cards=[],
            inline_explanations={}
        )
        
        self.state.current_card.regions.append(self.state.current_region)
        
        if self.verbose:
            logger.info(f"开始区域: {region_name}")
        
        return None
    
    def _process_label(self, match: re.Match, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理标签"""
        if not self.state.current_card:
            logger.warning(f"行 {self.state.line_number}: 标签必须在卡片内部")
            return None
        
        symbol = match.group(1)
        content_text = match.group(2).strip()
        
        # 解析标签内容（逗号分隔的列表）
        content_items = [item.strip() for item in content_text.split(',')]
        
        label = Label(
            symbol=symbol,
            content=content_items,
            label_type=self._determine_label_type(symbol)  # 将 type 改为 label_type
        )
        
        self.state.current_card.labels.append(label)
        
        if self.verbose:
            logger.info(f"添加标签: {symbol}: {content_text}")
        
        return None
    
    def _process_code_block_start(self, match: re.Match, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理代码块开始"""
        language = match.group(1).strip() or "text"
        self.state.in_code_block = True
        self.state.code_block_language = language
        self.state.code_block_content = []
        
        if self.verbose:
            logger.info(f"开始代码块: {language}")
        
        return None
    
    def _process_code_block_line(self, line: str, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理代码块内的行"""
        # 检查代码块结束
        if self.PATTERNS['code_block_end'].match(line):
            return self._process_code_block_end(all_lines, current_index)
        
        # 添加内容到代码块
        self.state.code_block_content.append(line)
        return None
    
    def _process_code_block_end(self, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理代码块结束"""
        if self.state.code_block_content and self.state.current_region:
            # 创建代码块区域
            code_content = '\n'.join(self.state.code_block_content)
            
            # 将代码块添加到当前区域
            if self.state.current_region.content:
                self.state.current_region.content += '\n\n```' + self.state.code_block_language + '\n'
                self.state.current_region.content += code_content + '\n```'
            else:
                self.state.current_region.content = '```' + self.state.code_block_language + '\n'
                self.state.current_region.content += code_content + '\n```'
            
            # 添加到行列表
            self.state.current_region.lines.append('```' + self.state.code_block_language)
            self.state.current_region.lines.extend(self.state.code_block_content)
            self.state.current_region.lines.append('```')
        
        # 重置代码块状态
        self.state.in_code_block = False
        self.state.code_block_language = ""
        self.state.code_block_content = None
        
        if self.verbose:
            logger.info("结束代码块")
        
        return None
    
    def _process_line(self, line: str, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理单行内容 - 修复版"""
        line_str = line.rstrip('\r')  # 确保是字符串
        
        # 处理代码块
        if self.state.in_code_block:
            return self._process_code_block_line(line_str, all_lines, current_index)
        
        # 检查各种模式
        for pattern_name, pattern in self.PATTERNS.items():
            match = pattern.match(line_str)
            if match:
                # 获取处理方法
                method_name = f"_process_{pattern_name}"
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    return method(match, all_lines, current_index)
                else:
                    # 如果没有对应的处理方法，记录警告并使用默认处理
                    if self.verbose:
                        logger.warning(f"行 {self.state.line_number}: 模式 '{pattern_name}' 没有对应的处理方法")
                    break  # 跳出循环，使用默认处理
        
        # 默认处理 - 传递字符串而不是match对象
        return self._process_default(line_str, all_lines, current_index)
        
    def _extract_vibe_cards_from_line(self, line: str, source_card: str, line_number: int) -> Tuple[str, List[VibeCard]]:
        """从行中提取注卡"""
        vibe_cards = []
        
        def replace_vibe(match):
            content = match.group(1).strip()
            annotation = match.group(2).strip()
            
            vibe_card = VibeCard(
                content=content,
                annotation=annotation,
                source_card=source_card,
                line_number=line_number
            )
            vibe_cards.append(vibe_card)
            
            # 返回替换后的内容（可以添加特殊标记）
            return f"`{content}`"
        
        # 替换所有注卡标记
        processed_line = self.PATTERNS['vibe_card'].sub(replace_vibe, line)
        
        return processed_line, vibe_cards
    
    def _extract_archive_description(self, all_lines: List[str], current_index: int) -> str:
        """提取归档描述（归档定义后的注释）"""
        description = ""
        next_line_index = current_index + 1
        
        while next_line_index < len(all_lines):
            next_line = all_lines[next_line_index].strip()
            if self.PATTERNS['comment'].match(next_line):
                # 移除注释符号并添加描述
                comment_content = re.sub(r'^\s*#\s*', '', next_line)
                if description:
                    description += " " + comment_content
                else:
                    description = comment_content
                next_line_index += 1
            else:
                break
        
        return description
    
    def _extract_card_metadata(self, all_lines: List[str], current_index: int) -> Dict[str, Any]:
        """提取卡片元数据（卡片开始后的注释）"""
        metadata = {}
        next_line_index = current_index + 1
        
        while next_line_index < len(all_lines):
            next_line = all_lines[next_line_index].strip()
            comment_match = self.PATTERNS['comment'].match(next_line)
            if comment_match:
                # 解析元数据注释，如 # 标签: 值
                comment_content = re.sub(r'^\s*#\s*', '', next_line)
                if ':' in comment_content:
                    key, value = comment_content.split(':', 1)
                    metadata[key.strip()] = value.strip()
                next_line_index += 1
            else:
                break
        
        return metadata
    
    def _determine_label_type(self, symbol: str) -> str:
        """根据符号确定标签类型"""
        label_types = {
            '!': 'important',
            '?': 'question', 
            '>': 'reference',
            '<': 'backlink',
            'i': 'info',
            '✓': 'completed',
            '☆': 'star',
            '▲': 'priority'
        }
        return label_types.get(symbol, 'default')
    
    def _process_default(self, line: str, all_lines: List[str], current_index: int) -> Optional[int]:
        """处理默认文本行 - 修复版"""
        # 确保line是字符串
        if hasattr(line, 'string'):  # 如果是re.Match对象
            line_str = line.string
        else:
            line_str = str(line)
        
        # 空行处理

        if not line_str.strip():
            return None
        
        # 注释行处理
        if self.PATTERNS['comment'].match(line_str):
            return None
        
        # 添加到当前区域
        if self.state.current_region:
            if self.state.current_region.content:
                self.state.current_region.content += "\n" + line_str
            else:
                self.state.current_region.content = line_str
            
            self.state.current_region.lines.append(line_str)
            
            # 处理行内解释
            explanation_match = self.PATTERNS['inline_explanation'].search(line_str)
            if explanation_match:
                # 可以在这里处理行内解释
                pass
            
            # 处理注卡
            vibe_cards = self._extract_vibe_cards_from_line(line_str, self.state.current_card.theme, len(self.state.current_region.lines))
            self.state.current_region.vibe_cards.extend(vibe_cards)
        
        return None
    

class VibeCardProcessor:
    """增强版注卡处理器"""
    
    def process(self, document: Document) -> Document:
        """处理文档中的所有注卡"""
        if not document.archives:
            return document
        
        all_vibe_cards = []
        vibe_main_cards = []
        
        # 收集所有注卡并生成主卡
        for archive in document.archives:
            for card in archive.cards:
                card_vibe_cards = self._extract_vibe_cards_from_card(card)
                all_vibe_cards.extend(card_vibe_cards)
                card.vibe_cards = card_vibe_cards
                
                # 为每个注卡生成主卡
                for vibe_card in card_vibe_cards:
                    main_card = self._create_main_card_from_vibe(vibe_card, card)
                    vibe_main_cards.append(main_card)
        
        # 创建注卡归档
        if vibe_main_cards:
            vibe_archive = VibeArchive(
                name="自动生成注卡",
                cards=vibe_main_cards,
                description=f"基于{len(all_vibe_cards)}个注卡自动生成"
            )
            document.vibe_archive = vibe_archive
        
        # 添加注卡链接关系
        self._add_vibe_links(document)
        
        return document
    
    def _extract_vibe_cards_from_card(self, card: MainCard) -> List[VibeCard]:
        """从卡片中提取所有注卡"""
        vibe_cards = []
        
        for region in card.regions:
            region_vibe_cards = self._extract_vibe_cards_from_region(region, card.theme)
            vibe_cards.extend(region_vibe_cards)
            region.vibe_cards = region_vibe_cards
        
        return vibe_cards
    
    def _extract_vibe_cards_from_region(self, region: Region, source_card: str) -> List[VibeCard]:
        """从区域中提取注卡"""
        vibe_cards = []
        
        # 从区域内容中提取
        content_vibe_cards = self._extract_vibe_cards_from_text(region.content, source_card)
        vibe_cards.extend(content_vibe_cards)
        
        # 从行中提取（保留行号信息）
        for i, line in enumerate(region.lines):
            line_vibe_cards = self._extract_vibe_cards_from_text(line, source_card, i)
            for vibe in line_vibe_cards:
                vibe.line_number = i  # 设置准确的行号
            vibe_cards.extend(line_vibe_cards)
        
        return vibe_cards
    
    def _extract_vibe_cards_from_text(self, text: str, source_card: str, line_number: int = 0) -> List[VibeCard]:
        """从文本中提取注卡"""
        vibe_cards = []
        pattern = re.compile(r'`([^`]+)`\[([^\]]+)\]')
        
        for match in pattern.finditer(text):
            content = match.group(1).strip()
            annotation = match.group(2).strip()
            
            vibe_card = VibeCard(
                content=content,
                annotation=annotation,
                source_card=source_card,
                line_number=line_number
            )
            vibe_cards.append(vibe_card)
        
        return vibe_cards
    
    def _create_main_card_from_vibe(self, vibe_card: VibeCard, source_card: MainCard) -> MainCard:
        """从注卡创建详细的主卡"""
        # 创建返回链接标签
        backlink_label = Label(
            symbol="←",
            content=[f"#{source_card.theme}"],
            label_type="backlink"
        )
        
        # 创建内容区域
        content_region = Region(
            name="内容",
            content=vibe_card.content,
            lines=[vibe_card.content]
        )
        
        # 创建批注区域
        annotation_region = Region(
            name="批注", 
            content=vibe_card.annotation,
            lines=[vibe_card.annotation]
        )
        
        # 创建来源区域
        source_info = f"来自卡片: {source_card.theme}"
        if vibe_card.line_number > 0:
            source_info += f" (第{vibe_card.line_number + 1}行)"
        
        source_region = Region(
            name="来源",
            content=source_info,
            lines=[source_info]
        )
        
        # 创建上下文区域（如果源卡片有相关区域）
        context_region = self._create_context_region(vibe_card, source_card)
        
        regions = [content_region, annotation_region, source_region]
        if context_region:
            regions.append(context_region)
        
        # 创建主卡
        main_card = MainCard(
            theme=vibe_card.content,
            labels=[backlink_label],
            regions=regions,
            vibe_cards=[],  # 注卡生成的主卡不再包含注卡
            metadata={
                "source_card": source_card.theme,
                "line_number": vibe_card.line_number,
                "generated_from": "vibe_card"
            }
        )
        
        return main_card
    
    def _create_context_region(self, vibe_card: VibeCard, source_card: MainCard) -> Optional[Region]:
        """创建上下文区域，显示注卡在源卡片中的上下文"""
        if not vibe_card.line_number or vibe_card.line_number <= 0:
            return None
        
        # 查找源区域
        source_region = None
        for region in source_card.regions:
            if vibe_card.line_number < len(region.lines):
                source_region = region
                break
        
        if not source_region:
            return None
        
        # 提取上下文（前后各2行）
        start_line = max(0, vibe_card.line_number - 2)
        end_line = min(len(source_region.lines), vibe_card.line_number + 3)
        
        context_lines = source_region.lines[start_line:end_line]
        highlighted_lines = []
        
        for i, line in enumerate(context_lines, start_line):
            if i == vibe_card.line_number:
                highlighted_lines.append(f"> {line}  ← 注卡位置")
            else:
                highlighted_lines.append(f"  {line}")
        
        context_content = "\n".join(highlighted_lines)
        
        return Region(
            name="上下文",
            content=context_content,
            lines=highlighted_lines
        )
    
    def _add_vibe_links(self, document: Document):
        """添加注卡之间的链接关系"""
        # 收集所有注卡主题
        vibe_themes = set()
        if document.vibe_archive:
            for card in document.vibe_archive.cards:
                vibe_themes.add(card.theme.lower())
        
        # 在主卡中查找对注卡的引用
        for archive in document.archives:
            for card in archive.cards:
                for region in card.regions:
                    # 在内容中查找注卡引用
                    for theme in vibe_themes:
                        if theme.lower() in region.content.lower():
                            # 添加引用标签
                            ref_label = Label(
                                symbol="→",
                                content=[f"#{theme}"],
                                label_type="vibe_reference"
                            )
                            card.labels.append(ref_label)
                            break


# 向后兼容的别名
Parser = RemUpParser

# 使用示例
if __name__ == "__main__":
    # 测试解析器
    sample_code = """
--<英语学习>--
# 这是一个归档注释

<+vigilant
# 标签: 重点词汇
(!: 重点词汇)
(>: #careful, #watchful, 近义词)

---解释
adj. 警惕的；警觉的；戒备的
`vigilant`[来自拉丁语vigilare，意为"保持清醒"] >>形容词

---词组
- be vigilant about/against/over >>对…保持警惕
- remain/stay vigilant >>保持警惕

---例句
- Citizens are urged to remain vigilant against `网络诈骗`[指通过互联网进行的欺诈行为]。 >>敦促公民对网络诈骗保持警惕
- The security guard must be vigilant at all times. >>保安必须时刻保持警觉。
/+
"""
    
    parser = RemUpParser(verbose=True)
    try:
        document = parser.parse(sample_code)
        print("解析成功!")
        print(f"归档数: {len(document.archives)}")
        for archive in document.archives:
            print(f"  归档: {archive.name}")
            for card in archive.cards:
                print(f"    卡片: {card.theme}")
                print(f"      标签: {len(card.labels)}")
                print(f"      区域: {len(card.regions)}")
    except Exception as e:
        print(f"解析错误: {e}")