
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

# RemUp - Memory Enhancement Markup Language

**Transform structured knowledge into interactive learning cards**

![GitHub Actions](https://img.shields.io/badge/Python-3.8+-blue)
![GitHub Actions](https://img.shields.io/badge/License-MIT-green)

#Project Introduction • #Quick Start • #Syntax Guide • #Examples • #Contributing

</div>

## 📖 Project Introduction

RemUp is an innovative lightweight markup language and compiler designed to build a "learn-understand-relearn" memory loop. It converts structured knowledge into interactive HTML learning cards with rich functionality, supporting main cards, annotation cards, and intelligent archiving to help users efficiently build personal knowledge systems.

### ✨ Core Features

- **🎴 Main Card System** - Structured knowledge representation using concise markup syntax
- **💡 Annotation Card System** - Interactive annotations with hover display and bidirectional navigation
- **📚 Archiving System** - Intelligent knowledge organization with automatic navigation generation
- **🎨 Responsive Design** - Perfect adaptation across multiple devices with print support
- **🔗 Smart Links** - Quick navigation between tags to build knowledge networks
- **🖱️ Drag & Drop Compilation** - File drag support for one-click compilation experience

## 🚀 Quick Start

### System Requirements

- Python 3.8 or higher
- Modern browser (Chrome, Firefox, Safari, etc.)

### Installation Steps

1. **Clone Repository**
```bash
git clone 链接1.git
cd PPL_Project-RemUp
```

2. **Enter Compiler Directory**
```bash
cd RemUp_Compiler
```

3. **Create Virtual Environment (Recommended)**
```bash
python -m venv venv
# Activate environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
```

4. **Install Dependencies**
```bash
pip install -e .
```

5. **Verify Installation**
```bash
remup --help
```

## 💡 Usage

### 1. Command Line Compilation (Recommended)

Use the `remup` command for compilation:

```bash
# Compile single file
remup examples/vocabulary.remup

# Compile entire directory
remup examples/ -d

# Specify output file
remup examples/vocabulary.remup -o my_notes.html

# Use custom CSS style
remup examples/vocabulary.remup -c custom_style.css
```

### 2. Drag & Drop Compilation (Convenient Method)

Drag `.remup` files onto the `compile_remup.py` script for automatic compilation:

1. Locate the `compile_remup.py` file
2. Drag any `.remup` file onto the script
3. The script automatically compiles, generating output files in the same directory

**Features:**
- ✅ Automatic file type detection
- ✅ Output files generated in same directory as source
- ✅ Batch file support
- ✅ Detailed compilation logs

### 3. Python API Integration

```python
from remup.compiler import compile_remup

# Basic compilation
result_path = compile_remup("my_notes.remup")
print(f"Compilation completed: {result_path}")

# Advanced options
result_path = compile_remup(
    "my_notes.remup", 
    "output.html",
    css_file="custom_style.css"
)
```

## 📝 Syntax Guide

### Quick Syntax Reference

| Syntax Element | Format | Example | Description |
|---------------|--------|---------|-------------|
| **Main Card Start** | `<+Topic` | `<+python_functions` | Define new card |
| **Main Card End** | `/+>` | `/+>` | End current card |
| **Tags** | `(symbol: content)` | `(!: Important)` | Top-right corner tags |
| **Link Tags** | `(symbol: #target)` | `(>: #function)` | Navigable tags |
| **Section Division** | `---SectionName` | `---Example` | Content partitioning |
| **Inline Explanation** | `>>explanation` | `Python>>Programming Language` | Gray explanation text |
| **Annotation Cards** | `` `content`[annotation] `` | `` `variable`[Stores data] `` | Interactive annotations |
| **Archive Markers** | `--<Topic>--` | `--<Programming Basics>--` | Card grouping |

### Complete Example

```remup
--<Programming Learning>--
<+python_functions
(>: #variable, #class)
(!: Basic Concepts)

---Definition
`Function`[Reusable code block for specific tasks] >>Programming Basics
Fundamental unit for organizing code, improving reusability and readability.

---Syntax
      ```python
      def greet(name: str) -> str:
         return f"Hello, {name}!"
      ```

---Examples
- Use `def` keyword to define functions
- Function names should be descriptive, using lowercase and underscores
- Include type annotations for better code readability
- Use docstrings to document function purpose

---Best Practices
1. Maintain single responsibility principle
2. Limit function parameters (typically ≤3)
3. Use meaningful function and parameter names
4. Write docstrings for complex functions
/+>
```

## 📁 Project Structure

```
RemUp_Compiler/
├── remup/                 # Compiler core package
│   ├── __init__.py
│   ├── main.py           # Command line entry point
│   ├── cli.py            # 🔥 New: CLI interface
│   ├── compiler.py       # Compiler coordinator
│   ├── lexer.py          # Lexical analyzer
│   ├── parser.py         # Syntax parser
│   ├── ast_nodes.py      # AST node definitions
│   └── html_generator.py # HTML generator
├── compile_remup.py      # 🔥 New: Drag & drop compilation script
├── examples/             # Example files
│   ├── vocabulary.remup
│   ├── programming.remup
│   └── concepts.remup
├── tests/                # Test cases
├── setup.py              # Package configuration
├── requirements.txt      # Dependencies list
└── README.md            # Project documentation
```

## 🛠️ Development Guide

### Running Tests

```bash
# Enter compiler directory
cd RemUp_Compiler

# Run test suite
python -m pytest tests/

# Run specific tests
python -m pytest tests/test_compiler.py
```

### Project Architecture

RemUp compiler follows standard compiler architecture:

1. **Lexical Analysis** (`lexer.py`) - Converts source code to token stream
2. **Syntax Analysis** (`parser.py`) - Builds Abstract Syntax Tree (AST)
3. **Code Generation** (`html_generator.py`) - Transforms AST to HTML
4. **Compiler Coordination** (`compiler.py`) - Orchestrates compilation pipeline

### Extension Development

Welcome to extend RemUp functionality:

- **New Syntax Elements** - Add support in lexer and parser
- **Output Formats** - Implement new generators (PDF, Anki, etc.)
- **Theme System** - Create switchable CSS themes

## 🤝 Contributing Guidelines

We welcome contributions in all forms!

### How to Contribute

1. **Fork** this repository
2. **Create feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Development Focus Areas

- Syntax parser improvements and optimization
- Annotation card interaction enhancements
- Template system design and implementation
- Export format extensions (PDF, Anki, etc.)
- Performance optimization and error handling

## ❓ Frequently Asked Questions

### Q: What if drag & drop compilation doesn't work?
A: Ensure:
1. Python is installed and environment variables are configured
2. Dependencies are installed via `pip install -e .`
3. File extension is `.remup`

### Q: How to customize output styles?
A: Create custom CSS file and specify with `-c` parameter:
```bash
remup my_notes.remup -c custom_style.css
```

### Q: Annotation cards not displaying?
A: Check annotation syntax format: `` `content`[annotation] ``, ensure backticks wrap content and brackets wrap annotations.

### Q: Tag navigation not working?
A: Ensure target exists, tag format is `(>: #target_id)`, and `target_id` matches actual card topic.

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Contact

- **Author**: MingShuo-S
- **Email**: 2954809209@qq.com
- **Project Link**: 链接1
- **Issue Reporting**: Welcome to submit issues and suggestions via GitHub Issues

## 🙏 Acknowledgments

Thanks to all developers who contributed to this project! Special thanks to:

- All testers and bug reporters
- Users who provided valuable feedback
- Open source community for inspiration and support

---

<div align="center">

If this project helps you, please consider giving it a ⭐️!

**Start your memory enhancement journey!** 🚀

</div>