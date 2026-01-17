#!/bin/bash
echo "🔄 开始安装RemUp编译器..."

# 检查Python版本
python --version || { echo "❌ Python未安装"; exit 1; }

# 卸载旧版本
echo "🧹 卸载旧版本..."
pip uninstall -y remup 2>/dev/null || true

# 安装新版本
echo "📦 安装新版本..."
pip install -e .

# 验证安装
echo "✅ 验证安装..."
if python -c "import remup; print('🚀 RemUp版本:', remup.__version__)" 2>/dev/null; then
    echo "✅ RemUp安装成功!"
    
    # 测试命令行
    if remup --version 2>/dev/null; then
        echo "✅ 命令行工具工作正常"
    else
        echo "⚠️  命令行工具可能有问题"
    fi
else
    echo "❌ 安装失败"
    exit 1
fi

echo ""
echo "🎉 安装完成!"
echo "💡 使用示例:"
echo "   remup --help                  # 查看帮助"
echo "   remup init                    # 初始化项目"
echo "   remup example.ru -o output    # 编译文件"
echo ""
echo "📖 文档: https://github.com/MingShuo-S/PPL_Project-RemUp/tree/main"