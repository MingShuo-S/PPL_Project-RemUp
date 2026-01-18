<!-- 语言切换器 -->
<div align="right">
  <small>
    🌐 <strong>Language: </strong> 
    <a href="README.md">中文</a> • 
    <a href="README_eng.md">English</a>
  </small>
</div>

# RemUp - Memory-Assisted Markup Language

<div align="center">
<div align="center">
<a href="https://github.com/MingShuo-S/PPL_Project-RemUp">
    <img src="Logo.svg" alt="RemUp Logo" width="500" height="120" style="border-radius: 8px;  object-fit: cover;object-position: center; 
border: 0px solid #ddd;">
  </a>

**Transform structured knowledge into interactive learning cards**




#-project-overview • #-quick-start • #-syntax-guide • #-usage-examples • #-contributing

</div>

## 📖 Project Overview

RemUp is an innovative lightweight markup language and compiler designed to build a "learn-understand-relearn" memory loop. It transforms structured knowledge into interactive HTML learning cards with features like main cards, annotation cards, and intelligent archiving to help users efficiently build personal knowledge systems.

### ✨ Key Features

- **🎴 Main Card System** - Structured knowledge representation with clean markup syntax
- **💡 Annotation Card System** - Interactive annotations with hover effects and bidirectional navigation
- **📚 Archive System** - Intelligent knowledge organization with automatic navigation
- **🎨 Responsive Design** - Perfect display across devices with print support
- **🔗 Smart Linking** - Quick navigation between tags, building knowledge networks

## 🚀 Quick Start

### System Requirements

- Python 3.8 or higher
- Modern browser (Chrome, Firefox, Safari, etc.)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/MingShuo-S/PPL_Project-RemUp.git
   cd PPL_Project-RemUp
   ```

2. **Enter the compiler directory**
   ```bash
   cd RemUp_Compiler  # Important: All source code is in this subdirectory
   ```

3. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   # Activate environment
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify installation**
   ```bash
   remup --help
   ```

## 📝 Syntax Guide

### Basic Syntax Cheat Sheet

| Element | Format | Example | Description |
|---------|--------|---------|-------------|
| **Card Start** | `<+Theme` | `<+python_functions` | Define new card |
| **Card End** | `/+>` | `/+>` | End current card |
| **Label** | `(symbol: content)` | `(!: Important)` | Top-right label |
| **Link Label** | `(symbol: #target)` | `(>: #function)` | Clickable label |
| **Region** | `---RegionName` | `---Examples` | Content section |
| **Inline Explanation** | `>>explanation` | `Python>>programming` | Gray explanation text |
| **Annotation Card** | `` `content`[annotation] `` | `` `variable`[stores data] `` | Interactive annotation |
| **Archive Marker** | `--<Theme>--` | `--<Programming Basics>--` | Card grouping |

### Complete Example

```remup
--<Programming Learning>--
<+python_functions
(>: #variable, #class)
(!: Basic Concepts)

---Definition
`Function`[Reusable code block for specific tasks] >>Programming Basics
A fundamental unit for organizing code, improving reusability and readability.

---Syntax
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

---Examples
- Use `def` keyword to define functions
- Function names should be descriptive, using lowercase and underscores
- Include type annotations for better readability
- Use docstrings to document function purpose

---Best Practices
1. Keep functions single-purpose (Single Responsibility Principle)
2. Limit function parameters (typically no more than 3)
3. Use meaningful function and parameter names
4. Write docstrings for complex functions
/+
```

## 💡 Usage Examples

### Basic Usage

```bash
# Compile single .ru file (execute in RemUp_Compiler directory)
remup examples/vocabulary.ru

# Specify output file
rem up examples/vocabulary.ru -o my_notes.html

# Use custom CSS styling
rem up examples/vocabulary.ru -c custom_style.css
```

### Python API Usage

```python
from remup import compile_remup

# Basic compilation
result_path = compile_remup("my_notes.ru")
print(f"Compilation complete: {result_path}")

# Advanced options
result_path = compile_remup(
    "my_notes.ru", 
    "output.html",
    css_file="custom_style.css"
)
```

### Project Structure

```
RemUp/                          # Main repository root
│
├── RemUp_Compiler/             # 🔥 Compiler main directory (users need to enter here)
│   ├── remup/                 # Python package source code
│   │   ├── __init__.py        # Package initialization
│   │   ├── lexer.py           # Lexical analyzer
│   │   ├── parser.py          # Syntax parser
│   │   ├── compiler.py        # Compiler core
│   │   └── html_generator.py  # HTML generator
│   ├── examples/              # Example files
│   ├── tests/                 # Test cases
│   ├── requirements.txt       # Python dependencies
│   └── setup.py              # Package installation configuration
│
└── README.md                 # Project documentation
```

## 🛠️ Development Guide

### Running Tests

```bash
# Enter compiler directory
cd RemUp_Compiler

# Run test suite
python -m pytest tests/

# Run specific test
python -m pytest tests/test_basic.py
```

### Project Architecture

RemUp compiler follows standard compiler architecture:

1. **Lexical Analysis** (`lexer.py`) - Convert source code to token stream
2. **Syntax Analysis** (`parser.py`) - Build Abstract Syntax Tree (AST)
3. **Code Generation** (`html_generator.py`) - Transform AST to HTML
4. **Compiler Coordination** (`compiler.py`) - Coordinate compilation process

### Extension Development

Welcome to extend RemUp functionality:

- **New Syntax Elements** - Add support in lexer and parser
- **Output Formats** - Implement new generators (PDF, Anki, etc.)
- **Theme System** - Create switchable CSS themes

## 🤝 Contributing

We welcome all forms of contributions!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Focus

- Improvement and optimization of syntax parser
- Enhancement of annotation card interactions
- Design and implementation of template system
- Extension of export formats (PDF, Anki, etc.)
- Performance optimization and error handling

## ❓ Frequently Asked Questions

### Q: Why do I need to execute commands in the RemUp_Compiler directory?
A: Because all source code and configuration files are located in the `RemUp_Compiler` subdirectory, which is the root of the Python package.

### Q: What to do if I get module import errors?
A: Make sure:
1. You are in the `RemUp_Compiler` directory
2. Virtual environment is activated
3. You have run `pip install -e .`

### Q: How to customize styles?
A: Create a custom CSS file and specify it with the `-c` parameter:
```bash
remup my_notes.ru -c custom_style.css
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

- **Author**: MingShuo-S
- **Email**: 2954809209@qq.com
- **Project Link**: https://github.com/MingShuo-S/PPL_Project-RemUp
- **Issue Reporting**: Welcome to submit issues and suggestions via GitHub Issues

## 🙏 Acknowledgments

Thanks to all developers who have contributed to this project! Special thanks to:

- All testers and bug reporters
- Users who provided valuable feedback
- The open-source community for inspiration and support

---

<div align="center">

If this project is helpful to you, please consider giving it a ⭐️!

**Start your memory upgrade journey now!** 🚀

</div>

---

<div align="right">
  <small>
    🌐 <strong>Language:</strong> 
    <a href="README.md">中文</a> • 
    <a href="README_eng.md">English</a>
  </small>
</div>