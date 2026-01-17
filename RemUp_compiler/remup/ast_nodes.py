"""
完整的AST节点定义 - 包含注点系统
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any  # 添加 Dict, Any 导入

@dataclass
class VibeCard:
    """注点节点 - 表示行内批注"""
    content: str          # 注点内容（被标注的文本）
    annotation: str       # 批注内容
    source_card: str =""  # 来源卡片主题（哪个卡片包含这个注点）
    line_number: int = 0  # 行号（可选，用于精确定位）
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于模板渲染"""
        return {
            'content': self.content,
            'annotation': self.annotation,
            'source_card': self.source_card,
            'line_number': self.line_number
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
class Region:
    """区域节点"""
    name: str              # 区域名称
    content: str           # 区域内容文本
    lines: List[str] = field(default_factory=list)  # 按行存储的内容
    vibe_cards: List[VibeCard] = field(default_factory=list)  # 区域内的注点
    inline_explanations: dict = field(default_factory=dict)  # 行内解释 {行号: 解释}
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'content': self.content,
            'lines': self.lines,
            'vibe_cards': [vc.to_dict() for vc in self.vibe_cards],
            'inline_explanations': self.inline_explanations
        }

@dataclass
class MainCard:
    """主卡节点"""
    theme: str              # 卡片主题
    labels: List[Label]     # 标签列表
    regions: List[Region]   # 区域列表
    vibe_cards: List[VibeCard] = field(default_factory=list)  # 卡片内的所有注点
    metadata: Dict[str, Any] = field(default_factory=dict)   # 添加metadata字段
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'theme': self.theme,
            'labels': [label.to_dict() for label in self.labels],
            'regions': [region.to_dict() for region in self.regions],
            'vibe_cards': [vc.to_dict() for vc in self.vibe_cards],
            'metadata': self.metadata  # 添加metadata到字典
        }

@dataclass
class VibeArchive:
    """注点归档节点 - 存储自动生成的注点主卡"""
    name: str = "自动生成注点"
    cards: List[MainCard] = field(default_factory=list)  # 由注点生成的主卡
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'cards': [card.to_dict() for card in self.cards]
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
    archives: List[Archive]                # 归档列表
    vibe_archive: Optional[VibeArchive] = None  # 注点归档（可选）
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'archives': [archive.to_dict() for archive in self.archives],
            'vibe_archive': self.vibe_archive.to_dict() if self.vibe_archive else None
        }