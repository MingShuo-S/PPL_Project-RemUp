"""
高级模板引擎 - 支持模板文件加载和复杂模板语法
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json

class AdvancedTemplateEngine:
    """高级模板引擎 - 支持模板继承、包含、过滤器等高级功能"""
    
    def __init__(self, template_dir: str = "templates", cache_templates: bool = True):
        """
        初始化模板引擎
        
        Args:
            template_dir: 模板目录路径
            cache_templates: 是否缓存模板
        """
        self.template_dir = Path(template_dir)
        self.cache_templates = cache_templates
        self.template_cache = {}
        self.filters = self._register_default_filters()
        
        # 确保模板目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板文件名或模板内容
            context: 模板上下文数据
            
        Returns:
            渲染后的HTML内容
        """
        # 加载模板
        template_content = self._load_template(template_name)
        
        if not template_content:
            raise ValueError(f"模板不存在或为空: {template_name}")
        
        # 预处理模板（处理继承和包含）
        processed_template = self._preprocess_template(template_content, context)
        
        # 渲染模板
        result = self._render_template(processed_template, context)
        
        return result
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        从字符串渲染模板
        
        Args:
            template_string: 模板字符串
            context: 模板上下文数据
            
        Returns:
            渲染后的HTML内容
        """
        return self._render_template(template_string, context)
    
    def _load_template(self, template_name: str) -> Optional[str]:
        """加载模板文件"""
        # 如果已经在缓存中，直接返回
        if self.cache_templates and template_name in self.template_cache:
            return self.template_cache[template_name]
        
        # 检查是否是模板内容而不是文件名
        if '\n' in template_name or '{{' in template_name:
            return template_name
        
        # 构建模板文件路径
        template_path = self.template_dir / template_name
        if not template_path.suffix:
            template_path = template_path.with_suffix('.html')
        
        # 检查文件是否存在
        if not template_path.exists():
            # 尝试在子目录中查找
            html_files = list(self.template_dir.glob("**/*.html"))
            for file_path in html_files:
                if file_path.stem == template_path.stem:
                    template_path = file_path
                    break
            else:
                raise FileNotFoundError(f"模板文件不存在: {template_path}")
        
        # 读取模板内容
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 缓存模板
            if self.cache_templates:
                self.template_cache[template_name] = content
            
            return content
            
        except Exception as e:
            raise IOError(f"无法读取模板文件 {template_path}: {e}")
    
    def _preprocess_template(self, template: str, context: Dict[str, Any]) -> str:
        """预处理模板（处理继承、包含等）"""
        result = template
        
        # 处理模板继承 {% extends "base.html" %}
        result = self._process_extends(result, context)
        
        # 处理模板包含 {% include "header.html" %}
        result = self._process_includes(result, context)
        
        # 处理块定义 {% block content %} ... {% endblock %}
        result = self._process_blocks(result, context)
        
        return result
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """渲染模板内容"""
        result = template
        
        # 处理变量替换 {{ variable }}, {{ variable|filter }}
        result = self._process_variables(result, context)
        
        # 处理for循环 {% for item in items %} ... {% endfor %}
        result = self._process_for_loops(result, context)
        
        # 处理if条件 {% if condition %} ... {% elif %} ... {% else %} ... {% endif %}
        result = self._process_if_conditions(result, context)
        
        # 处理注释 {# ... #}
        result = self._process_comments(result)
        
        return result
    
    def _process_extends(self, template: str, context: Dict[str, Any]) -> str:
        """处理模板继承"""
        pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
        
        def replace_extends(match):
            parent_template = match.group(1)
            
            try:
                # 加载父模板
                parent_content = self._load_template(parent_template)
                
                # 提取当前模板中的块内容
                blocks = self._extract_blocks(template)
                
                # 在父模板中替换块内容
                for block_name, block_content in blocks.items():
                    block_pattern = r'{%\s*block\s+' + re.escape(block_name) + r'\s*%}.*?{%\s*endblock\s*%}'
                    replacement = f"{{% block {block_name} %}}{block_content}{{% endblock %}}"
                    parent_content = re.sub(block_pattern, replacement, parent_content, flags=re.DOTALL)
                
                return parent_content
                
            except Exception as e:
                return f"<!-- 模板继承错误: {e} -->"
        
        return re.sub(pattern, replace_extends, template, flags=re.IGNORECASE)
    
    def _process_includes(self, template: str, context: Dict[str, Any]) -> str:
        """处理模板包含"""
        pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
        
        def replace_include(match):
            include_template = match.group(1)
            
            try:
                # 加载包含的模板
                include_content = self._load_template(include_template)
                
                # 渲染包含的模板
                return self._render_template(include_content, context)
                
            except Exception as e:
                return f"<!-- 包含模板错误: {e} -->"
        
        return re.sub(pattern, replace_include, template, flags=re.IGNORECASE)
    
    def _extract_blocks(self, template: str) -> Dict[str, str]:
        """提取模板中的块定义"""
        blocks = {}
        pattern = r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}'
        
        for match in re.finditer(pattern, template, re.DOTALL):
            block_name = match.group(1)
            block_content = match.group(2).strip()
            blocks[block_name] = block_content
        
        return blocks
    
    def _process_blocks(self, template: str, context: Dict[str, Any]) -> str:
        """处理块定义（在继承中已处理，这里主要清理未使用的块）"""
        # 移除未被替换的块定义
        pattern = r'{%\s*block\s+\w+\s*%}.*?{%\s*endblock\s*%}'
        return re.sub(pattern, '', template, flags=re.DOTALL)
    
    def _process_variables(self, template: str, context: Dict[str, Any]) -> str:
        """处理变量替换，支持过滤器和复杂表达式"""
        # 匹配 {{ variable }}, {{ variable|filter }}, {{ variable|filter(arg) }}
        pattern = r'{{\s*([^}|]+?)(?:\s*\|\s*([^}]+))?\s*}}'
        
        def replace_variable(match):
            variable_expr = match.group(1).strip()
            filter_expr = match.group(2) if match.group(2) else None
            
            try:
                # 获取变量值
                value = self._get_variable_value(variable_expr, context)
                
                # 应用过滤器
                if filter_expr:
                    value = self._apply_filter(value, filter_expr)
                
                return str(value) if value is not None else ""
                
            except Exception as e:
                return f"<!-- 变量错误: {variable_expr} -->"
        
        return re.sub(pattern, replace_variable, template)
    
    def _get_variable_value(self, expression: str, context: Dict[str, Any]) -> Any:
        """获取变量值，支持点符号访问"""
        parts = expression.split('.')
        value = context
        
        for part in parts:
            part = part.strip()
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                # 尝试作为方法调用（无参数）
                if callable(value):
                    try:
                        value = value()
                    except:
                        value = None
                else:
                    value = None
                break
        
        return value
    
    def _apply_filter(self, value: Any, filter_expr: str) -> Any:
        """应用过滤器"""
        filters = [f.strip() for f in filter_expr.split('|')]
        
        for filter_name in filters:
            if ':' in filter_name:
                filter_name, args = filter_name.split(':', 1)
                args = [arg.strip() for arg in args.split(',')]
            else:
                args = []
            
            filter_name = filter_name.strip()
            
            if filter_name in self.filters:
                try:
                    value = self.filters[filter_name](value, *args)
                except Exception as e:
                    # 过滤器应用失败，保持原值
                    continue
            else:
                # 未知过滤器，尝试作为字符串方法调用
                if hasattr(str, filter_name) and callable(getattr(str, filter_name)):
                    try:
                        value = getattr(str(value), filter_name)()
                    except:
                        pass
        
        return value
    
    def _process_for_loops(self, template: str, context: Dict[str, Any]) -> str:
        """处理for循环，支持嵌套和循环变量"""
        pattern = r'{%\s*for\s+(\w+)\s+in\s+([^%]+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_loop(match):
            item_var = match.group(1).strip()
            collection_expr = match.group(2).strip()
            loop_body = match.group(3)
            
            try:
                # 获取集合
                collection = self._get_variable_value(collection_expr, context)
                
                if not collection or not hasattr(collection, '__iter__'):
                    return f"<!-- 错误: {collection_expr} 不是可迭代对象 -->"
                
                result_parts = []
                loop_length = len(collection) if hasattr(collection, '__len__') else 0
                
                for index, item in enumerate(collection):
                    # 创建循环上下文
                    loop_context = context.copy()
                    loop_context[item_var] = item
                    loop_context['loop'] = {
                        'index': index + 1,
                        'index0': index,
                        'first': index == 0,
                        'last': index == loop_length - 1,
                        'length': loop_length
                    }
                    
                    # 渲染循环体
                    rendered_item = self._render_template(loop_body, loop_context)
                    result_parts.append(rendered_item)
                
                return ''.join(result_parts)
                
            except Exception as e:
                return f"<!-- 循环错误: {e} -->"
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    def _process_if_conditions(self, template: str, context: Dict[str, Any]) -> str:
        """处理if条件，支持elif和else"""
        # 匹配if-elif-else结构
        pattern = r'{%\s*if\s+([^%]+?)\s*%}(.*?)(?:{%\s*elif\s+([^%]+?)\s*%}(.*?))*(?:{%\s*else\s*%}(.*?))?{%\s*endif\s*%}'
        
        def replace_condition(match):
            condition_groups = match.groups()
            conditions = []
            else_content = None
            
            # 提取条件和对应内容
            for i in range(0, len(condition_groups) - 1, 2):
                condition_expr = condition_groups[i]
                condition_content = condition_groups[i + 1] if i + 1 < len(condition_groups) else None
                
                if condition_expr and condition_content:
                    conditions.append((condition_expr.strip(), condition_content.strip()))
                elif condition_expr == '' and condition_content:
                    else_content = condition_content.strip()
                    break
            
            # 评估条件
            for condition_expr, condition_content in conditions:
                if self._evaluate_condition(condition_expr, context):
                    return self._render_template(condition_content, context)
            
            # 如果所有条件都不满足，返回else内容
            if else_content:
                return self._render_template(else_content, context)
            
            return ""
        
        return re.sub(pattern, replace_condition, template, flags=re.DOTALL)
    
    def _evaluate_condition(self, condition_expr: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式"""
        # 简单条件评估，支持变量存在性检查、比较操作等
        condition_expr = condition_expr.strip()
        
        # 检查变量是否存在且为真
        if condition_expr in context:
            value = context[condition_expr]
            return bool(value)
        
        # 支持简单的比较操作
        comparison_ops = ['==', '!=', '<', '>', '<=', '>=']
        for op in comparison_ops:
            if op in condition_expr:
                left, right = condition_expr.split(op, 1)
                left = left.strip()
                right = right.strip()
                
                left_val = self._get_variable_value(left, context) if '.' in left else context.get(left, left)
                right_val = self._get_variable_value(right, context) if '.' in right else context.get(right, right)
                
                # 尝试类型转换
                try:
                    if isinstance(left_val, str) and right_val.isdigit():
                        right_val = int(right_val)
                    elif isinstance(right_val, str) and left_val.isdigit():
                        left_val = int(left_val)
                except:
                    pass
                
                # 执行比较
                if op == '==':
                    return left_val == right_val
                elif op == '!=':
                    return left_val != right_val
                elif op == '<':
                    return left_val < right_val
                elif op == '>':
                    return left_val > right_val
                elif op == '<=':
                    return left_val <= right_val
                elif op == '>=':
                    return left_val >= right_val
        
        # 默认检查变量是否存在且为真
        value = self._get_variable_value(condition_expr, context)
        return bool(value) if value is not None else False
    
    def _process_comments(self, template: str) -> str:
        """处理模板注释 {# ... #}"""
        pattern = r'{#.*?#}'
        return re.sub(pattern, '', template, flags=re.DOTALL)
    
    def _register_default_filters(self) -> Dict[str, callable]:
        """注册默认过滤器"""
        return {
            'lower': lambda x, *args: str(x).lower(),
            'upper': lambda x, *args: str(x).upper(),
            'title': lambda x, *args: str(x).title(),
            'capitalize': lambda x, *args: str(x).capitalize(),
            'length': lambda x, *args: len(x) if hasattr(x, '__len__') else 0,
            'default': lambda x, default_val='', *args: x if x is not None else default_val,
            'join': lambda x, separator=',', *args: separator.join(str(i) for i in x) if hasattr(x, '__iter__') else str(x),
            'slice': lambda x, start=0, end=None, *args: x[int(start):int(end)] if end else x[int(start):],
            'safe': lambda x, *args: x,  # 标记为安全HTML（不转义）
            'escape': lambda x, *args: self._escape_html(str(x)),
            'truncate': lambda x, length=50, ellipsis='...', *args: 
                str(x)[:int(length)] + (ellipsis if len(str(x)) > int(length) else ''),
            'date': lambda x, format_str='%Y-%m-%d', *args: 
                x.strftime(format_str) if hasattr(x, 'strftime') else str(x),
            'json': lambda x, *args: json.dumps(x, ensure_ascii=False),
        }
    
    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        escape_chars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        for char, replacement in escape_chars.items():
            text = text.replace(char, replacement)
        return text
    
    def add_filter(self, name: str, filter_func: callable):
        """添加自定义过滤器"""
        self.filters[name] = filter_func
    
    def clear_cache(self):
        """清空模板缓存"""
        self.template_cache.clear()


# 向后兼容的简单版本
class SimpleTemplateEngine(AdvancedTemplateEngine):
    """简化版模板引擎 - 保持向后兼容"""
    
    def __init__(self, template_dir: str = "templates"):
        super().__init__(template_dir, cache_templates=True)
    
    def render(self, template: str, context: Dict[str, Any]) -> str:
        """简化版渲染方法，兼容旧代码"""
        # 如果template看起来像是文件内容而不是文件名，直接渲染
        if '{{' in template or '{%' in template:
            return self.render_string(template, context)
        else:
            return super().render(template, context)


# 使用示例
if __name__ == "__main__":
    # 测试模板引擎
    engine = AdvancedTemplateEngine("templates")
    
    # 测试上下文
    context = {
        "page_title": "测试页面",
        "archives": [
            {
                "name": "归档1",
                "cards": [
                    {"theme": "卡片1", "content": "内容1"},
                    {"theme": "卡片2", "content": "内容2"}
                ]
            }
        ],
        "user": {"name": "张三", "age": 25},
        "show_details": True
    }
    
    # 测试模板渲染
    test_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ page_title }}</title>
    </head>
    <body>
        <h1>{{ page_title|upper }}</h1>
        
        {% if show_details %}
        <div class="details">
            <p>用户: {{ user.name }}, 年龄: {{ user.age }}</p>
        </div>
        {% endif %}
        
        {% for archive in archives %}
        <div class="archive">
            <h2>{{ archive.name }}</h2>
            <ul>
                {% for card in archive.cards %}
                <li>{{ card.theme }}: {{ card.content }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    result = engine.render_string(test_template, context)
    print("模板渲染测试:")
    print(result)