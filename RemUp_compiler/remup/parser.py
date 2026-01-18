import re
from typing import List, Tuple, Optional, Dict, Any
from remup.ast_nodes import (
    Document, Archive, MainCard, Region, Label, 
    VibeCard, Inline_Explanation, Rem_List, Code_Block, VibeArchive
)

class Parser:
    """语法分析器 - 完整修复注卡解析问题"""
    
    def __init__(self, tokens: List[Tuple[str, str, int]], source_name: str = "Generated Document"):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
        self.vibe_card_counter = 1
        self.source_name = source_name
        
        # 解析状态
        self.current_archive = None
        self.current_card = None
        self.current_region = None
        self.current_list = None
        
    def advance(self):
        """前进到下一个token"""
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Tuple[str, str, int]]:
        """查看前方第offset个token"""
        peek_pos = self.position + offset
        if 0 <= peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def parse(self) -> Document:
        """解析整个文档"""
        archives = []
        
        # 自动生成标题
        if self.source_name.endswith('.remup'):
            title = self.source_name[:-6]
        else:
            title = self.source_name
        
        # 解析文档内容
        while self.current_token:
            token_type, token_value, _ = self.current_token
            
            if token_type == 'ARCHIVE':
                archive = self.parse_archive()
                if archive:
                    archives.append(archive)
                    self.current_archive = archive
            elif token_type == 'CARD_START':
                card = self.parse_card()
                if card:
                    # 确保卡片有归属的归档
                    if not archives:
                        default_archive = Archive("Default", [])
                        archives.append(default_archive)
                        self.current_archive = default_archive
                    self.current_archive.cards.append(card)
            else:
                self.advance()
        
        # 构建注卡归档
        vibe_archive = self.build_vibe_archive(archives)
        
        return Document(title, archives, vibe_archive)
    
    def parse_archive(self) -> Optional[Archive]:
        """解析归档定义"""
        if not self.current_token or self.current_token[0] != 'ARCHIVE':
            return None
        
        archive_name = self.current_token[1]
        self.advance()
        return Archive(archive_name, [])
    
    def parse_card(self) -> Optional[MainCard]:
        """解析卡片定义"""
        if not self.current_token or self.current_token[0] != 'CARD_START':
            return None
        
        theme = self.current_token[1]
        self.advance()
        
        # 解析标签
        labels = self.parse_labels()
        
        # 初始化卡片
        card = MainCard(theme, labels, [])
        self.current_card = card
        
        # 解析区域
        while self.current_token and self.current_token[0] != 'CARD_END':
            if self.current_token[0] == 'REGION':
                region = self.parse_region()
                if region:
                    card.regions.append(region)
            else:
                self.advance()
        
        # 消费卡片结束标记
        if self.current_token and self.current_token[0] == 'CARD_END':
            self.advance()
            
        return card
    
    def parse_labels(self) -> List[Label]:
        """解析标签列表"""
        labels = []
        
        while self.current_token and self.current_token[0] == 'LABEL':
            label_str = self.current_token[1]
            self.advance()
            
            if ':' in label_str:
                symbol, content_str = label_str.split(':', 1)
                symbol = symbol.strip()
                content_list = [c.strip() for c in content_str.split(',')]
                
                label = Label(symbol, content_list, "default")
                labels.append(label)
        
        return labels
    
    def parse_region(self) -> Optional[Region]:
        """解析区域定义 - 核心修复"""
        if not self.current_token or self.current_token[0] != 'REGION':
            return None
        
        region_name = self.current_token[1]
        self.advance()
        
        region = Region(region_name, "", [])
        self.current_region = region
        
        # 解析区域内容
        while self.current_token and self.current_token[0] not in ['REGION', 'CARD_END']:
            token_type, token_value, _ = self.current_token
            
            if token_type == 'TEXT':
                self.parse_text_line(region)
            elif token_type == 'VIBE_CARD':
                self.parse_vibe_card(region)
            elif token_type == 'INLINE_EXPLANATION':
                self.parse_inline_explanation(region)
            elif token_type in ['UNORDERED_LIST_ITEM', 'ORDERED_LIST_ITEM']:
                self.parse_list_item(region, token_type)
            elif token_type == 'CODE_BLOCK_START':
                self.parse_code_block(region)
            else:
                self.advance()
        
        # 更新区域内容
        region.content = '\n'.join(region.lines)
        return region
    
    def parse_text_line(self, region: Region):
        """解析文本行"""
        if not self.current_token or self.current_token[0] != 'TEXT':
            return
        
        content = self.current_token[1]
        region.lines.append(content)
        self.advance()
    
    def parse_vibe_card(self, region: Region):
        """解析注卡 - 关键修复"""
        if not self.current_token or self.current_token[0] != 'VIBE_CARD':
            return
        
        content = self.current_token[1]
        
        # 解析注卡内容：格式为"内容[批注]"
        match = re.match(r'([^\[\]]+)\[([^\]]+)\]', content)
        if match:
            card_content = match.group(1).strip()
            annotation = match.group(2).strip()
            
            vibe_card = VibeCard(
                id=self.vibe_card_counter,
                content=card_content,
                annotation=annotation,
                source_card=self.current_card.theme if self.current_card else ""
            )
            
            # 添加到区域和卡片
            region.vibe_cards.append(vibe_card)
            if self.current_card:
                self.current_card.vibe_cards.append(vibe_card)
            
            # 在区域行中添加注卡内容
            region.lines.append(card_content)
            
            self.vibe_card_counter += 1
        
        self.advance()
    
    def parse_inline_explanation(self, region: Region):
        """解析行内解释"""
        if not self.current_token or self.current_token[0] != 'INLINE_EXPLANATION':
            return
        
        content = self.current_token[1]
        
        # 关联到前一行
        if region.lines:
            last_line_index = len(region.lines) - 1
            last_line_content = region.lines[last_line_index]
            inline_explanation = Inline_Explanation(last_line_content, content)
            region.inline_explanations[last_line_index] = inline_explanation
        
        self.advance()
    
    def parse_list_item(self, region: Region, list_type: str):
        """解析列表项"""
        if not self.current_token or self.current_token[0] not in ['UNORDERED_LIST_ITEM', 'ORDERED_LIST_ITEM']:
            return
        
        content = self.current_token[1]
        
        # 检查内容中是否包含注卡
        vibe_cards = []
        match = re.match(r'([^\[\]]+)\[([^\]]+)\]', content)
        if match:
            card_content = match.group(1).strip()
            annotation = match.group(2).strip()
            
            vibe_card = VibeCard(
                id=self.vibe_card_counter,
                content=card_content,
                annotation=annotation,
                source_card=self.current_card.theme if self.current_card else ""
            )
            vibe_cards.append(vibe_card)
            self.vibe_card_counter += 1
            
            # 用内容替换标记
            content = card_content
        
        # 添加到区域行
        region.lines.append(content)
        
        # 处理注卡
        if vibe_cards:
            region.vibe_cards.extend(vibe_cards)
            if self.current_card:
                self.current_card.vibe_cards.extend(vibe_cards)
        
        self.advance()
    
    def parse_code_block(self, region: Region):
        """解析代码块"""
        if not self.current_token or self.current_token[0] != 'CODE_BLOCK_START':
            return
        
        language = self.current_token[1]
        self.advance()
        
        code_lines = []
        
        # 收集代码内容直到代码块结束
        while self.current_token and self.current_token[0] != 'CODE_BLOCK_END':
            if self.current_token[0] == 'CODE_BLOCK_CONTENT':
                code_lines.append(self.current_token[1])
            self.advance()
        
        # 消费代码块结束标记
        if self.current_token and self.current_token[0] == 'CODE_BLOCK_END':
            self.advance()
        
        # 创建代码块节点
        if code_lines:
            code_content = '\n'.join(code_lines)
            code_block = Code_Block(language, code_content)
            
            # 将代码块作为特殊行添加到区域
            region.lines.append(f"CODE_BLOCK:{language}")
    
    def build_vibe_archive(self, archives: List[Archive]) -> Optional[VibeArchive]:
        """构建注卡归档"""
        all_vibe_cards = []
        
        # 收集所有注卡
        for archive in archives:
            for card in archive.cards:
                all_vibe_cards.extend(card.vibe_cards)
        
        if not all_vibe_cards:
            return None
        
        # 按源卡片分组
        cards_by_source = {}
        for vibe_card in all_vibe_cards:
            source = vibe_card.source_card
            if source not in cards_by_source:
                cards_by_source[source] = []
            cards_by_source[source].append(vibe_card)
        
        # 为每个源卡片创建主卡
        vibe_archive_cards = []
        for source, cards in cards_by_source.items():
            # 创建区域来存放注卡内容
            region_content = []
            for card in cards:
                region_content.append(f"{card.content}")
            
            region = Region(f"注卡内容 - {source}", "\n".join(region_content), region_content)
            # 添加注卡到区域
            region.vibe_cards.extend(cards)
            
            main_card = MainCard(f"注卡: {source}", [], [region])
            # 添加注卡到卡片
            main_card.vibe_cards.extend(cards)
            vibe_archive_cards.append(main_card)
        
        return VibeArchive("注卡归档", vibe_archive_cards)

def print_ast(node, indent=0):
    """打印AST结构（用于调试）"""
    indent_str = "  " * indent
    
    if isinstance(node, Document):
        print(f"{indent_str}Document(title='{node.title}')")
        for archive in node.archives:
            print_ast(archive, indent + 1)
        if node.vibe_archive:
            print_ast(node.vibe_archive, indent + 1)
        else:
            print(f"{indent_str}VibeArchive: None")
    
    elif isinstance(node, Archive):
        print(f"{indent_str}Archive(name='{node.name}', cards={len(node.cards)})")
        for card in node.cards:
            print_ast(card, indent + 2)
    
    elif isinstance(node, MainCard):
        print(f"{indent_str}MainCard(theme='{node.theme}', labels={len(node.labels)}, regions={len(node.regions)}, vibe_cards={len(node.vibe_cards)})")
        for label in node.labels:
            print_ast(label, indent + 3)
        for region in node.regions:
            print_ast(region, indent + 3)
    
    elif isinstance(node, Region):
        print(f"{indent_str}Region(name='{node.name}', lines={len(node.lines)}, vibe_cards={len(node.vibe_cards)}, inline_explanations={len(node.inline_explanations)})")
        for i, line in enumerate(node.lines):
            print(f"{indent_str}  Line {i}: {line[:50]}{'...' if len(line) > 50 else ''}")
        for vibe_card in node.vibe_cards:
            print_ast(vibe_card, indent + 4)
        for line_idx, explanation in node.inline_explanations.items():
            print(f"{indent_str}  InlineExplanation[line={line_idx}]: {explanation.content[:30]}...")
    
    elif isinstance(node, Label):
        print(f"{indent_str}Label(symbol='{node.symbol}', content={node.content})")
    
    elif isinstance(node, VibeCard):
        print(f"{indent_str}VibeCard(id={node.id}, content='{node.content}', annotation='{node.annotation}')")
    
    elif isinstance(node, VibeArchive):
        print(f"{indent_str}VibeArchive(name='{node.name}', cards={len(node.cards)})")
        for card in node.cards:
            print_ast(card, indent + 2)

# 测试代码
if __name__ == "__main__":
    from lexer import Lexer
    
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
    
    # 词法分析
    lexer = Lexer()
    tokens = lexer.tokenize(test_code)
    
    print("词法分析结果:")
    for token in tokens:
        print(f"{token[0]:25} {token[1]}")
    
    # 语法分析
    parser = Parser(tokens, "test.remup")
    ast = parser.parse()
    
    print("\n" + "="*60)
    print("AST结构:")
    print("="*60)
    print_ast(ast)
    
    # 检查注卡解析结果
    print("\n" + "="*60)
    print("注卡解析检查:")
    print("="*60)
    
    total_vibe_cards = 0
    for archive in ast.archives:
        for card in archive.cards:
            total_vibe_cards += len(card.vibe_cards)
            if card.vibe_cards:
                print(f"卡片 '{card.theme}' 中的注卡:")
                for vibe_card in card.vibe_cards:
                    print(f"  - 内容: {vibe_card.content}")
                    print(f"    批注: {vibe_card.annotation}")
    
    print(f"\n总注卡数量: {total_vibe_cards}")
    print(f"注卡归档: {'存在' if ast.vibe_archive else '不存在'}")
    
    if ast.vibe_archive:
        print(f"注卡归档中的卡片数量: {len(ast.vibe_archive.cards)}")