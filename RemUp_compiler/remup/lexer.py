import re
from typing import List, Tuple, Optional

class Lexer:
    """
    词法分析器 - 根据语法规则将输入文本分解为词法标记
    """
    
    # 定义词法规则（正则表达式模式）
    PATTERNS = {
        'archive': re.compile(r'^--<([^>]+)>--\s*$'),
        'card_start': re.compile(r'^<\+([^/]+)\s*$'),
        'card_end': re.compile(r'^/\+>\s*$'),
        'label': re.compile(r'\(([^:]+):\s*([^)]+)\)'),
        'region': re.compile(r'^---\s*([^\s].*?)\s*$'),
        'vibe_card': re.compile(r'`([^`\n]+)`\[([^\]]*)\]'),
        'inline_explanation': re.compile(r'>>\s*([^\n]+?)\s*$'),
        'code_block_start': re.compile(r'^```\s*(\w*)\s*$'),
        'code_block_end': re.compile(r'^```\s*$'),
        'ordered_list': re.compile(r'^\d+\.\s+(.*)$'),
        'unordered_list': re.compile(r'^-\s+(.*)$'),
        'bold_text': re.compile(r'\*\*(.*?)\*\*'),
        'empty_line': re.compile(r'^\s*$')
    }
    
    def __init__(self):
        self.tokens = []
        self.current_line_num = 0
        self.in_code_block = False
        self.current_code_block_lang = ""
        self.current_code_block_content = []
    
    def tokenize(self, text: str) -> List[Tuple[str, str, int]]:
        """
        将输入文本分解为词法标记
        
        Args:
            text: 输入文本
            
        Returns:
            List[Tuple[str, str, int]]: 词法标记列表 (类型, 值, 行号)
        """
        self.tokens = []
        self.current_line_num = 0
        self.in_code_block = False
        lines = text.split('\n')
        
        for line in lines:
            self.current_line_num += 1
            self._process_line(line)
        
        return self.tokens
    
    def _process_line(self, line: str):
        """处理单行文本"""
        
        # 处理代码块状态
        if self.in_code_block:
            if self.PATTERNS['code_block_end'].match(line):
                # 结束代码块
                if self.current_code_block_content:
                    code_content = '\n'.join(self.current_code_block_content)
                    self.tokens.append(('CODE_BLOCK_CONTENT', code_content, self.current_line_num - len(self.current_code_block_content)))
                
                self.tokens.append(('CODE_BLOCK_END', '', self.current_line_num))
                self.in_code_block = False
                self.current_code_block_content = []
            else:
                # 在代码块中，收集内容
                self.current_code_block_content.append(line)
            return
        
        # 检查空行
        if self.PATTERNS['empty_line'].match(line):
            self.tokens.append(('EMPTY_LINE', '', self.current_line_num))
            return
        
        # 检查代码块开始
        code_start_match = self.PATTERNS['code_block_start'].match(line)
        if code_start_match:
            self.tokens.append(('CODE_BLOCK_START', code_start_match.group(1), self.current_line_num))
            self.in_code_block = True
            self.current_code_block_lang = code_start_match.group(1)
            self.current_code_block_content = []
            return
        
        # 检查归档定义
        archive_match = self.PATTERNS['archive'].match(line)
        if archive_match:
            self.tokens.append(('ARCHIVE', archive_match.group(1), self.current_line_num))
            return
        
        # 检查卡片开始
        card_start_match = self.PATTERNS['card_start'].match(line)
        if card_start_match:
            self.tokens.append(('CARD_START', card_start_match.group(1), self.current_line_num))
            return
        
        # 检查卡片结束
        card_end_match = self.PATTERNS['card_end'].match(line)
        if card_end_match:
            self.tokens.append(('CARD_END', '', self.current_line_num))
            return
        
        # 检查区域定义
        region_match = self.PATTERNS['region'].match(line)
        if region_match:
            self.tokens.append(('REGION', region_match.group(1), self.current_line_num))
            return
        
        # 处理行内元素（标签、注卡、行内解释、列表等）
        self._process_inline_elements(line)
    
    def _process_inline_elements(self, line: str):
        """处理行内的各种元素（完整修复版）"""
        # 首先检查是否是标签（标签通常独立成行）
        label_match = self.PATTERNS['label'].match(line)
        if label_match:
            symbol = label_match.group(1).strip()
            content = [c.strip() for c in label_match.group(2).split(',')]
            self.tokens.append(('LABEL', f"{symbol}:{','.join(content)}", self.current_line_num))
            return
        
        # 检查列表项（有序和无序）
        ordered_match = self.PATTERNS['ordered_list'].match(line)
        unordered_match = self.PATTERNS['unordered_list'].match(line)
        
        if ordered_match or unordered_match:
            # 提取列表项内容
            list_content = ordered_match.group(1) if ordered_match else unordered_match.group(1)
            
            # 标记列表项开始
            list_type = 'ORDERED_LIST_ITEM' if ordered_match else 'UNORDERED_LIST_ITEM'
            self.tokens.append((list_type, '', self.current_line_num))
            
            # 处理列表项内容中的行内元素
            self._process_line_content(list_content)
            return
        
        # 处理普通行内容
        self._process_line_content(line)

    def _process_line_content(self, content: str):
        """处理行内容中的各种行内元素"""
        remaining = content.strip()
        
        while remaining:
            # 1. 检查注卡
            vibe_card_match = self.PATTERNS['vibe_card'].search(remaining)
            if vibe_card_match:
                # 添加注卡前的文本（如果有）
                before_text = remaining[:vibe_card_match.start()].strip()
                if before_text:
                    self.tokens.append(('TEXT', before_text, self.current_line_num))
                
                # 添加注卡
                card_content = vibe_card_match.group(1)
                annotation = vibe_card_match.group(2)
                self.tokens.append(('VIBE_CARD', f"{card_content}[{annotation}]", self.current_line_num))
                
                # 更新剩余内容
                remaining = remaining[vibe_card_match.end():].strip()
                continue
            
            # 2. 检查行内解释
            inline_exp_match = self.PATTERNS['inline_explanation'].search(remaining)
            if inline_exp_match:
                # 添加行内解释前的文本（如果有）
                before_text = remaining[:inline_exp_match.start()].strip()
                if before_text:
                    self.tokens.append(('TEXT', before_text, self.current_line_num))
                
                # 添加行内解释
                explanation = inline_exp_match.group(1)
                self.tokens.append(('INLINE_EXPLANATION', explanation, self.current_line_num))
                
                # 更新剩余内容
                remaining = remaining[inline_exp_match.end():].strip()
                continue
            
            # 3. 检查加粗文本
            bold_match = self.PATTERNS['bold_text'].search(remaining)
            if bold_match:
                # 添加加粗文本前的文本（如果有）
                before_text = remaining[:bold_match.start()].strip()
                if before_text:
                    self.tokens.append(('TEXT', before_text, self.current_line_num))
                
                # 添加加粗文本
                bold_content = bold_match.group(1)
                self.tokens.append(('BOLD_TEXT', bold_content, self.current_line_num))
                
                # 更新剩余内容
                remaining = remaining[bold_match.end():].strip()
                continue
            
            # 4. 如果没有匹配到任何特殊模式，将剩余内容作为普通文本
            if remaining:
                self.tokens.append(('TEXT', remaining, self.current_line_num))
                break

def print_tokens(tokens):
    """打印词法分析结果"""
    print("词法分析结果:")
    print("-" * 50)
    for token_type, token_value, line_num in tokens:
        print(f"行 {line_num:3d}: {token_type:20} {token_value}")
    print("-" * 50)

# 测试代码
if __name__ == "__main__":
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
    lexer = Lexer()
    tokens = lexer.tokenize(test_code)
    print_tokens(tokens)