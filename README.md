
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
<a href="https://github.com/MingShuo-S/PPL_Project-RemUp">
    <img src="Logo.svg" alt="RemUp Logo" width="500" height="120" style="border-radius: 8px;  object-fit: cover;object-position: center; 
border: 0px solid #ddd;">
  </a>

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
   cd RemUp_Compiler  # 重要：所有源代码都在此子目录中
   ```

3. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   # 激活环境
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate     # Windows
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **验证安装**
   ```bash
   remup --help
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

## 💡 使用示例

### 基本使用

```bash
# 编译单个 .ru 文件（在 RemUp_Compiler 目录下执行）
remup examples/vocabulary.ru

# 指定输出文件
remup examples/vocabulary.ru -o my_notes.html

# 使用自定义CSS样式
remup examples/vocabulary.ru -c custom_style.css
```

### Python API 使用

```python
from remup import compile_remup

# 基本编译
result_path = compile_remup("my_notes.ru")
print(f"编译完成: {result_path}")

# 高级选项
result_path = compile_remup(
    "my_notes.ru", 
    "output.html",
    css_file="custom_style.css"
)
```

### 项目结构说明

```
RemUp/                          # 主仓库根目录
│
├── RemUp_Compiler/             # 🔥 编译器主目录（用户需要进入这里）
│   ├── remup/                 # Python包源代码
│   │   ├── __init__.py        # 包初始化
│   │   ├── lexer.py           # 词法分析器
│   │   ├── parser.py          # 语法解析器
│   │   ├── compiler.py        # 编译器核心
│   │   └── html_generator.py  # HTML生成器
│   ├── examples/              # 示例文件
│   ├── tests/                 # 测试用例
│   ├── requirements.txt       # Python依赖
│   └── setup.py              # 包安装配置
│
└── README.md                 # 项目说明文档
```

## 🛠️ 开发指南

### 运行测试

```bash
# 进入编译器目录
cd RemUp_Compiler

# 运行测试套件
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_basic.py
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

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发重点

- 语法解析器的完善和优化
- 注卡交互功能的增强
- 模板系统的设计与实现
- 导出格式的扩展（PDF、Anki等）
- 性能优化和错误处理

## ❓ 常见问题

### Q: 为什么需要在 RemUp_Compiler 目录下执行命令？
A: 因为所有源代码和配置文件都位于 `RemUp_Compiler` 子目录中，这是Python包的根目录。

### Q: 出现模块导入错误怎么办？
A: 确保：
1. 已在 `RemUp_Compiler` 目录中
2. 虚拟环境已激活
3. 已运行 `pip install -e .`

### Q: 如何自定义样式？
A: 创建自定义CSS文件，使用 `-c` 参数指定：
```bash
remup my_notes.ru -c custom_style.css
```

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