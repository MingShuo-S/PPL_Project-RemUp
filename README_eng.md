# RemUp

<!-- Language Switcher -->
<div align="right">
  <small>
    🌐 <strong>Language:</strong> 
    <a href="README.md">中文</a> • 
    <a href="README_eng.md">English</a>
  </small>
</div>

**RemUp** is an innovative lightweight markup language designed to build a "Learn-Understand-Relearn" memory loop.

## Table of Contents

- #core-concepts
- #syntax-quick-reference
- #complete-example
- #quick-start
- #installation--usage
- #project-structure
- #contributing
- #license
- #contact

## Core Concepts

### 🎴 Memory Unit System
RemUp organizes knowledge using "memory units" (cards). The core concepts of RemUp are as follows:
- **Main Card**: Structured knowledge container, defined using `<+topic` and `/+>`
- **Annotation Card**: Understanding enhancement tool, created using `` `content`[annotation] ``
- **Archive System**: Systematic review support, grouping cards using `--<topic>--`

### 🔄 Learning Loop Process
1. **Learn**: Create main cards to record core knowledge points
2. **Understand**: Add personal understanding and connections through annotation cards
3. **Relearn**: Conduct systematic review using link tags and archive system

## Syntax Quick Reference

| Syntax Element | Format | Function | Example |
|---------------|--------|----------|---------|
| **Main Card Start** | `<+topic` | Define memory unit | `<+vigilant` |
| **Main Card End** | `/+>` | End current card | `/+>` |
| **Tag** | `(symbol: content)` | Top-right corner tag | `(!: Important)` |
| **Link Tag** | `(symbol: #target, content)` | Clickable jump tag | `(>: #careful, Synonyms)` |
| **Section Division** | `---section_name` | Content partitioning | `---Examples` |
| **Inline Explanation** | `>>explanation` | Gray explanation text | `stay alert>>保持警惕` |
| **Annotation Card** | `` `content`[annotation] `` | Interactive annotation | `` `network`[internet] `` |
| **Archive Marker** | `--<topic>--` | Card grouping | `--<Key Vocabulary>--` |

## Complete Example

```remup
--<English Learning>--
<+vigilant
(>: #careful, #watchful, Synonyms)
(!: Key Vocabulary)

---Definition
adj. Watchful and alert to potential danger or difficulties
`vigilant`[From Latin vigilare, meaning "to keep awake"] >>adjective

---Phrases
- be vigilant about/against/over >>Remain watchful about
- remain/stay vigilant >>Continue to be watchful
- require vigilance >>Need watchfulness

---Examples
- Citizens are urged to remain vigilant against `cyber fraud`[Fraud conducted via internet]. >>Public advised to stay alert to online scams
- The security guard must be vigilant at all times. >>Security personnel should maintain constant watchfulness.
/+
```

## Quick Start

### 1. Create Your First Main Card

Create a `.ru` file (RemUp file):

```remup
<+python_function
(!: Programming Concept)

---Definition
`Function`[Code block performing specific task] >>function
is the basic unit for organizing code.

---Syntax
    ```python
    def greet(name):
        return f"Hello, {name}!"
    ```

---Explanation
- Use `def` keyword to define functions
- Function name followed by parentheses and parameters
- Function body indented, using `return` for output
/+
```

### 2. Add Interactive Annotation Cards

Add annotations to content that needs explanation:

```remup
In Python, `variables`[Data storage containers] are used to store data.
`Lists`[Ordered collections of elements] are commonly used data structures.
```

### 3. Organize Content with Archives

```remup
--<Python Basics>--
<+variable.../+>
<+function.../+>
<+list.../+>

--<Python Advanced>--
<+class.../+>
<+decorator.../+>
```

## Installation & Usage

### System Requirements
- Python 3.8 or higher

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/MingShuo-S/PPL_Project-RemUp.git
   cd PPL_Project-RemUp
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Compile RemUp File**
   ```bash
   python remup_compiler.py example.ru
   ```

## Project Structure

```
PPL_Project-RemUp/
├── src/                    # Source code directory
│   ├── compiler/          # RemUp compiler core
│   │   ├── parser.py      # Syntax parser
│   │   ├── transformer.py # AST transformer
│   │   └── generator.py   # HTML generator
│   ├── core/              # Core data types
│   │   ├── cards.py       # Card model definitions
│   │   └── annotations.py # Annotation system
│   └── utils/             # Utility functions
├── examples/              # Example files
│   ├── vocabulary.ru      # Vocabulary learning example
│   ├── programming.ru     # Programming concepts example
│   └── concepts.ru        # Concept learning example
├── templates/             # Output templates
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── README.md              # This README file
```

## Core Features Detailed

### 🎯 Main Card System
Main cards are the core knowledge carriers, supporting:
- **Structured Content**: Organize different sections through area division
- **Smart Tags**: Classification, importance level, relationship marking
- **Multimedia Support**: Rich content including code blocks, images, tables

### 💡 Annotation Card System
Annotation cards enable deep understanding:
- **Interactive Display**: Hover to view, click to fix
- **Automatic Archiving**: Each annotation generates independent main card, building knowledge network
- **Bidirectional Links**: Mutual references between annotations and main cards, forming knowledge graph

### 📚 Archive System
Archives support systematic learning:
- **Topic Classification**: Group by field, difficulty, type
- **Smart Navigation**: Automatically generate directories and navigation links
- **Review Planning**: Spaced repetition review based on archives

## Contributing

We welcome all contributions! Please see the guidelines below:

### How to Contribute
1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Focus
- Improvement and optimization of syntax parser
- Enhancement of annotation interaction features
- Design and implementation of template system
- Extension of export formats (PDF, Anki, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- **Author**: MingShuo-S
- **Email**: 2954809209@qq.com
- **Project Link**: https://github.com/MingShuo-S/PPL_Project-RemUp

---

If this project helps you, please consider giving it a ⭐️!

**Start your memory upgrade journey now!** 🚀