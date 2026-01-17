from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# 读取版本
version_path = Path(__file__).parent / "remup" / "__init__.py"
version = "1.0.0"
if version_path.exists():
    with open(version_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                version = line.split('=')[1].strip().strip('"\'')
                break

setup(
    name="remup",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="RemUp编译器 - 将.ru文件编译为HTML学习笔记",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['remup', 'remup.*']),
    package_data={
        'remup': [
            'templates/*.html',
            'static/css/*.css',
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        # 添加依赖项
    ],
    entry_points={
        'console_scripts': [
            'remup=remup.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="notes, compiler, learning, markdown, html",
    project_urls={
        "Source": "https://github.com/yourusername/remup",
        "Bug Reports": "https://github.com/yourusername/remup/issues",
    },
)