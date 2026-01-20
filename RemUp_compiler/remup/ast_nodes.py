"""
完整的AST节点定义 - 包含注点系统
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any  # 添加 Dict, Any 导入

@dataclass
class VibeCard:
    """注卡节点 - 表示行内批注"""
    id: int               # 注卡对应内容的id，用于往回跳转
    content: str          # 注卡内容（被标注的文本）
    annotation: str       # 批注内容
    source_card: str =""  # 来源卡片主题（哪个卡片包含这个注点）
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于模板渲染"""
        return {
            'id': self.id,
            'content': self.content,
            'annotation': self.annotation,
            'source_card': self.source_card,
        }

@dataclass
class Label:
    """标签节点"""
    symbol: str          # 标签符号（如"!"、">"、"?"等）
    content: List[str]   # 标签内容列表（可包含跳转链接如"#careful"）
    label_type: str = "default"  # 标签类型（default、important、warning等）
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'symbol': self.symbol,
            'content': self.content,
            'type': self.label_type
        }
    
@dataclass
class Inline_Explanation:
    """内联解释: 内联解释需要先展开整合到lines中,再对lines做进一步修饰"""
    line: str        # 内联解释所在行的文本
    content : str    # 内联解释的内容

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'line': self.line,
            'content': self.content
        }
    """内联解释要有对应的解释器，
    如果一行中出现了`>>`符号则说明这行包含内联解释，
    内联解释可以自动换行, 但不支持输入多行, 
    输入多行请用注卡"""

@dataclass
class ListItem:
    """列表项节点"""
    content: str                    # 列表项内容
    vibe_cards: List[VibeCard] = field(default_factory=list)  # 列表项中的注卡
    line_number: int = 0           # 原始行号（用于调试）
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'content': self.content,
            'vibe_cards': [vc.to_dict() for vc in self.vibe_cards],
            'line_number': self.line_number
        }

@dataclass
class Rem_List:
    """列表节点 - 修复列表处理"""
    list_type: str  # 'ul' 或 'ol'（无序或有序）
    items: List[ListItem] = field(default_factory=list)  # 列表项
    category: str = "unordered"  # 兼容旧版本：unordered/ordered
    
    def __post_init__(self):
        """初始化后处理，确保兼容性"""
        # 根据list_type设置category
        if self.list_type == 'ul':
            self.category = "unordered"
        elif self.list_type == 'ol':
            self.category = "unordered"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'list_type': self.list_type,
            'category': self.category,
            'items': [item.to_dict() for item in self.items],
            'lines': [item.content for item in self.items]  # 兼容旧版本
        }
    
@dataclass
class Code_Block:
    """代码块节点"""
    language: str         # 代码语言
    content: str          # 代码内容
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'language': self.language,
            'content': self.content
        }

@dataclass
class Region:
    """区域节点 - 修复列表处理"""
    name: str              # 区域名称
    content: str           # 区域内容文本
    lines: List[str] = field(default_factory=list)  # 按行存储的内容
    vibe_cards: List[VibeCard] = field(default_factory=list)  # 区域内的注点
    inline_explanations: Dict[int, Inline_Explanation] = field(default_factory=dict)  # 行内解释 {行号: 解释}
    lists: List[Rem_List] = field(default_factory=list)  # 新增：区域内的列表
    code_blocks: List[Code_Block] = field(default_factory=list)  # 新增：代码块
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'content': self.content,
            'lines': self.lines,
            'vibe_cards': [vc.to_dict() for vc in self.vibe_cards],
            'inline_explanations': {k: v.to_dict() for k, v in self.inline_explanations.items()},
            'lists': [lst.to_dict() for lst in self.lists],
            'code_blocks': [cb.to_dict() for cb in self.code_blocks]
        }
    
@dataclass
class MainCard:
    """主卡节点"""
    theme: str              # 卡片主题
    labels: List[Label]     # 标签列表
    regions: List[Region]   # 区域列表
    vibe_cards: List[VibeCard] = field(default_factory=list)  # 卡片内的所有注点
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'theme': self.theme,
            'labels': [label.to_dict() for label in self.labels],
            'regions': [region.to_dict() for region in self.regions],
            'vibe_cards': [vc.to_dict() for vc in self.vibe_cards],
        }

@dataclass
class VibeArchive:
    """注点归档节点 - 存储自动生成的注点主卡"""
    name: str = "注点归档"
    cards: List[MainCard] = field(default_factory=list)  # 由注点生成的主卡
    source_lines: List[str] = field(default_factory=list) # 由卡片转换器生成
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'cards': [card.to_dict() for card in self.cards],
            'sources_lines': [line for line in self.source_lines],
        }

@dataclass
class Archive:
    """归档节点"""
    name: str                  # 归档名称
    cards: List[MainCard]      # 主卡列表
    description: str = ""      # 归档描述（可选）
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'cards': [card.to_dict() for card in self.cards],
            'description': self.description
        }

@dataclass
class Document:
    """文档节点（根节点）"""
    title: str
    archives: List[Archive]                # 归档列表
    vibe_archive: Optional[VibeArchive] = None  # 注点归档（可选）
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'title': self.title,
            'archives': [archive.to_dict() for archive in self.archives],
            'vibe_archive': self.vibe_archive.to_dict() if self.vibe_archive else None
        }