#!/usr/bin/env python3
"""
AI-Drug Peptide V1.0 - Python包安装配置
AI驱动的肽类药物开发平台
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# 读取README文件
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "AI-Drug Peptide V1.0 - AI驱动的肽类药物开发平台"

# 读取requirements文件
def read_requirements():
    requirements_path = Path(__file__).parent / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

# 获取版本信息
def get_version():
    version_file = Path(__file__).parent / "src" / "__init__.py"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

# 获取长描述
long_description = read_readme()

# 获取依赖列表
install_requires = read_requirements()

setup(
    name="ai-drug-peptide",
    version=get_version(),
    author="AI-Drug Peptide Team",
    author_email="team@ai-drug-peptide.com",
    description="AI-driven peptide drug development platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xielab2017/AI-Drug-Peptide",
    project_urls={
        "Bug Reports": "https://github.com/xielab2017/AI-Drug-Peptide/issues",
        "Source": "https://github.com/xielab2017/AI-Drug-Peptide",
        "Documentation": "https://ai-drug-peptide.readthedocs.io/",
        "Download": "https://github.com/xielab2017/AI-Drug-Peptide/releases",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
            "black>=21.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "pre-commit>=2.0.0",
        ],
        "viz": [
            "plotly>=5.0.0",
            "networkx>=2.6.0",
            "bokeh>=2.0.0",
        ],
        "ml": [
            "torch>=1.9.0",
            "transformers>=4.0.0",
            "scikit-learn>=1.0.0",
        ],
        "bio": [
            "biopython>=1.79",
            "biopandas>=0.4.0",
            "pymol-open-source>=2.0.0",
        ],
        "workflow": [
            "prefect>=2.0.0",
            "dask>=2021.0.0",
            "celery>=5.0.0",
        ],
        "database": [
            "psycopg2-binary>=2.9.0",
            "neo4j>=4.4.0",
            "sqlalchemy>=1.4.0",
            "redis>=4.0.0",
        ],
        "all": [
            "plotly>=5.0.0",
            "networkx>=2.6.0",
            "torch>=1.9.0",
            "transformers>=4.0.0",
            "biopython>=1.79",
            "biopandas>=0.4.0",
            "prefect>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "neo4j>=4.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-drug-peptide=launch:main",
            "peptide-dashboard=dashboard:main",
            "peptide-install=install:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt", "*.md", "*.csv", "*.pdb"],
        "config": ["*.json", "*.yaml", "*.yml"],
        "data": ["*.csv", "*.json", "*.pdb"],
        "templates": ["*.html", "*.jinja2"],
    },
    zip_safe=False,
    keywords=[
        "bioinformatics",
        "peptide",
        "drug-discovery",
        "molecular-docking",
        "protein-interaction",
        "conservation-analysis",
        "ai",
        "machine-learning",
        "prefect",
        "workflow",
        "biochemistry",
        "pharmacology",
    ],
    platforms=["any"],
    license="MIT",
    maintainer="AI-Drug Peptide Team",
    maintainer_email="team@ai-drug-peptide.com",
    # 添加更多元数据
    download_url="https://github.com/xielab2017/AI-Drug-Peptide/archive/v1.0.0.tar.gz",
    # 支持的Python版本
    python_requires=">=3.8,<4.0",
    # 依赖链接
    dependency_links=[],
    # 测试套件
    test_suite="tests",
    # 测试要求
    tests_require=[
        "pytest>=6.0.0",
        "pytest-cov>=3.0.0",
        "pytest-mock>=3.6.0",
    ],
    # 命令行工具
    scripts=[
        "installers/install.sh",
        "installers/install.ps1",
    ],
    # 数据文件
    data_files=[
        ("config", ["config/config.json"]),
        ("installers", ["installers/install.sh", "installers/install.ps1"]),
    ],
)
