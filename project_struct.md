remup_compiler/
├── src/
│   ├── lexer.py          # 词法分析器
│   ├── parser.py         # 语法解析器
│   ├── ast.py           # 抽象语法树定义
│   ├── transformer.py   # AST转换器
│   ├── generator.py     # HTML生成器
│   ├── template_engine.py # 模板系统
│   └── utils.py         # 工具函数
├── templates/           # HTML模板
│   ├── base.html
│   ├── card.html
│   └── archive.html
├── static/             # 静态资源
│   └── css/
│       └── remup.css
├── examples/           # 示例文件
├── tests/             # 测试用例
└── main.py           # 主程序入口