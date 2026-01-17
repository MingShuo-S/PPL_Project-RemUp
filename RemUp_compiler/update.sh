#!/bin/bash
echo "🔄 开始更新RemUp编译器..."

# 备份当前版本
BACKUP_DIR="remup_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 备份当前版本到: $BACKUP_DIR"

# 创建备份
mkdir -p "$BACKUP_DIR"
cp -r remup/ templates/ static/ setup.py pyproject.toml "$BACKUP_DIR/" 2>/dev/null || true

# 拉取最新代码（如果是Git仓库）
if [ -d ".git" ]; then
    echo "⬇️  拉取最新代码..."
    git pull origin main
fi

# 重新安装
echo "🔧 重新安装..."
pip install -e . --upgrade

# 验证更新
if python -c "import remup; print('✅ 当前版本:', remup.__version__)" 2>/dev/null; then
    echo "🎉 更新成功!"
    
    # 显示版本变化
    if [ -f "$BACKUP_DIR/remup/__init__.py" ]; then
        OLD_VERSION=$(grep "__version__" "$BACKUP_DIR/remup/__init__.py" | cut -d'"' -f2)
        NEW_VERSION=$(python -c "import remup; print(remup.__version__)" 2>/dev/null)
        echo "📊 版本变化: $OLD_VERSION → $NEW_VERSION"
    fi
else
    echo "❌ 更新失败，正在恢复备份..."
    cp -r "$BACKUP_DIR"/* ./
    pip install -e .
    echo "✅ 已恢复备份版本"
    exit 1
fi

# 清理备份（保留最近3个）
echo "🧹 清理旧备份..."
ls -d remup_backup_* 2>/dev/null | sort -r | tail -n +4 | xargs rm -rf 2>/dev/null || true

echo "✨ 更新完成!"