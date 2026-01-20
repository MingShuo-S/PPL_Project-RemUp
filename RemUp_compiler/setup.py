#!/usr/bin/env python3
"""
RemUp编译器安装配置 v3.0
"""

from setuptools import setup, find_packages
import os

# 读取项目描述
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "RemUp编译器 - 将RemUp标记语言编译为交互式HTML笔记"

# 读取requirements.txt
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except:
        return []

setup(
    name="remup",
    version="3.0.0",
    author="MingShuo-S",
    author_email="2954809209@qq.com",
    description="RemUp编译器 - 将RemUp标记语言编译为交互式HTML笔记",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MingShuo-S/PPL_Project-RemUp",
    packages=find_packages(include=["remup", "remup.*"]),
    include_package_data=False,  # 不包含静态文件
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "remup=remup.main:main",
        ],
    },
    keywords="remup, markup, compiler, notes, html, css, theme",
    project_urls={
        "Bug Reports": "https://github.com/MingShuo-S/PPL_Project-RemUp/issues",
        "Source": "https://github.com/MingShuo-S/PPL_Project-RemUp",
    },
)

# 安装后消息
print("\n" + "="*50)
print("🎉 RemUp编译器安装完成!")
print("="*50)
print("💡 快速开始:")
print("  remup --help                    # 查看帮助")
print("  remup --list-themes            # 查看可用主题")
print("  remup example.remup            # 编译文件")
print("  remup example.remup -t DarkTheme  # 使用指定主题")
print("  remup ./notes -d               # 编译目录")
print("\n📁 注意：静态文件（CSS）需要从GitHub仓库手动复制到项目根目录下的static文件夹中。")
print("="*50)