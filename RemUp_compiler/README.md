
---
<!-- 语言切换器 -->
<div align="right">
  <small>
    🌐 <strong>Language: </strong> 
    <a href="README.md">中文</a> • 
    <a href="README_eng.md">English</a>
  </small>
</div>
<div align="center">


# RemUp - 记忆辅助标记语言

**将结构化的知识转换为交互式学习卡片**

![GitHub Actions](https://img.shields.io/badge/Python-3.8+-blue)
![GitHub Actions](https://img.shields.io/badge/License-MIT-green)

#项目介绍 • #快速开始 • #语法指南 • #使用示例 • #贡献指南

</div>

## 📖 项目介绍

RemUp 是一个创新的轻量级标记语言和编译器，专为构建"学习-理解-再学习"的记忆闭环而设计。它可以将结构化的知识转换为具有丰富交互功能的HTML学习卡片，支持主卡系统、注卡批注和智能归档，帮助用户高效构建个人知识体系。

### ✨ 核心特性

- **🎴 主卡系统** - 结构化知识承载，使用简洁的标记语法
- **💡 注卡系统** - 交互式批注，悬停显示，双向跳转
- **📚 归档系统** - 智能知识组织，自动生成导航
- **🎨 响应式设计** - 多设备完美适配，支持打印输出
- **🔗 智能链接** - 标签间快速跳转，构建知识网络
- **🖱️ 拖拽编译** - 支持文件拖拽，一键编译体验

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- 现代浏览器（Chrome、Firefox、Safari等）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/MingShuo-S/PPL_Project-RemUp.git
cd PPL_Project-RemUp
```

2. **进入编译器目录**
```bash
cd RemUp_Compiler
```

3. **创建虚拟环境（推荐）**
```bash
python -m venv venv
# 激活环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
```

4. **安装依赖**
```bash
pip install -e .
```

5. **验证安装**
```bash
remup --help
```

## 💡 使用方式

### 1. 命令行编译（推荐）

使用`remup`命令进行编译：

```bash
# 编译单个文件
remup examples/vocabulary.remup

# 编译整个目录
remup examples/ -d

# 指定输出文件
remup examples/vocabulary.remup -o my_notes.html

# 使用自定义CSS样式
remup examples/vocabulary.remup -c custom_style.css
```

### 2. 拖拽编译（便捷方式）

将`.remup`文件拖拽到`compile_remup.py`脚本上即可自动编译：

1. 定位到`compile_remup.py`文件
2. 将任意`.remup`文件拖拽到该脚本上
3. 脚本自动完成编译，输出文件在同目录生成

**特性：**
- ✅ 自动检测文件类型
- ✅ 输出文件与源文件同目录
- ✅ 批量文件支持
- ✅ 详细编译日志

### 3. Python API 调用

```python
from remup.compiler import compile_remup

# 基本编译
result_path = compile_remup("my_notes.remup")
print(f"编译完成: {result_path}")

# 高级选项
result_path = compile_remup(
    "my_notes.remup", 
    "output.html",
    css_file="custom_style.css"
)
```

## 📝 语法指南

### 基础语法速查表

| 语法元素 | 格式 | 示例 | 说明 |
|---------|------|------|------|
| **主卡开始** | `<+主题` | `<+python_functions` | 定义新卡片 |
| **主卡结束** | `/+>` | `/+>` | 结束当前卡片 |
| **标签** | `(符号: 内容)` | `(!: 重要)` | 右上角标签 |
| **链接标签** | `(符号: #目标)` | `(>: #function)` | 可跳转标签 |
| **区域划分** | `---区域名` | `---示例` | 内容分区 |
| **行内解释** | `>>解释` | `Python>>编程语言` | 灰色解释文字 |
| **注卡批注** | `` `内容`[批注] `` | `` `变量`[存储数据] `` | 交互式批注 |
| **归档标记** | `--<主题>--` | `--<编程基础>--` | 卡片分组 |

### 完整示例

```remup
--<编程学习>--
<+python_functions
(>: #variable, #class)
(!: 基础概念)

---定义
`函数`[完成特定功能的可重用代码块] >>编程基础
是组织代码的基本单元，提高代码的复用性和可读性。

---语法
      ```python
      def greet(name: str) -> str:
         return f"Hello, {name}!"
      ```

---示例
- 定义函数时使用 `def` 关键字
- 函数名应具有描述性，使用小写字母和下划线
- 包含类型注解提高代码可读性
- 使用文档字符串说明函数功能

---最佳实践
1. 保持函数功能单一（单一职责原则）
2. 限制函数参数数量（通常不超过3个）
3. 使用有意义的函数和参数名
4. 为复杂函数编写文档字符串
/+>
```

## 📁 项目结构

```
RemUp_Compiler/
├── remup/                 # 编译器核心包
│   ├── __init__.py
│   ├── main.py           # 命令行入口点
│   ├── cli.py            # 🔥 新增：CLI接口
│   ├── compiler.py       # 编译器协调器
│   ├── lexer.py          # 词法分析器
│   ├── parser.py         # 语法解析器
│   ├── ast_nodes.py      # AST节点定义
│   └── html_generator.py # HTML生成器
├── compile_remup.py      # 🔥 新增：拖拽编译脚本
├── examples/             # 示例文件
│   ├── vocabulary.remup
│   ├── programming.remup
│   └── concepts.remup
├── tests/                # 测试用例
├── setup.py              # 包配置
├── requirements.txt      # 依赖列表
└── README.md            # 项目说明
```

## 🛠️ 开发指南

### 运行测试

```bash
# 进入编译器目录
cd RemUp_Compiler

# 运行测试套件
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_compiler.py
```

### 项目架构

RemUp编译器采用标准的编译器架构：

1. **词法分析** (`lexer.py`) - 将源代码转换为token流
2. **语法分析** (`parser.py`) - 构建抽象语法树(AST)
3. **代码生成** (`html_generator.py`) - 将AST转换为HTML
4. **编译器协调** (`compiler.py`) - 协调整个编译流程

### 扩展开发

欢迎扩展RemUp的功能：

- **新的语法元素** - 在lexer和parser中添加支持
- **输出格式** - 实现新的生成器（如PDF、Anki等）
- **主题系统** - 创建可切换的CSS主题

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献方式

1. **Fork** 本仓库
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 开发重点

- 语法解析器的完善和优化
- 注卡交互功能的增强
- 模板系统的设计与实现
- 导出格式的扩展（PDF、Anki等）
- 性能优化和错误处理

## ❓ 常见问题

### Q: 拖拽编译不工作怎么办？
A: 确保：
1. 已安装Python并配置环境变量
2. 已运行 `pip install -e .` 安装依赖
3. 文件扩展名为 `.remup`

### Q: 如何自定义输出样式？
A: 创建自定义CSS文件，使用 `-c` 参数指定：
```bash
remup my_notes.remup -c custom_style.css
```

### Q: 注卡功能不显示怎么办？
A: 检查注卡语法格式：`` `内容`[批注] ``，确保使用反引号包裹内容，方括号包裹批注。

### Q: 标签跳转失效？
A: 确保跳转目标存在，标签格式为 `(>: #target_id)`，且 `target_id` 与实际卡片主题一致。

## 📄 许可证

本项目基于 MIT 许可证 - 查看 LICENSE 文件了解详情。

## 📞 联系方式

- **作者**: MingShuo-S
- **邮箱**: 2954809209@qq.com
- **项目链接**: https://github.com/MingShuo-S/PPL_Project-RemUp
- **问题反馈**: 欢迎通过GitHub Issues提交问题和建议

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！特别感谢：

- 所有测试人员和bug报告者
- 提供宝贵反馈的用户
- 开源社区的启发和支持

---

<div align="center">

如果这个项目对你有帮助，请考虑给它一个 ⭐️！

**开始你的记忆升级之旅吧！** 🚀

</div>