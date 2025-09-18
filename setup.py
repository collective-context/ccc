#!/usr/bin/env python3
"""
Setup script for cccmd - fallback for Debian packaging
"""

from setuptools import setup, find_packages

setup(
    name="cccmd",
    version="0.3.2",
    packages=find_packages(),
    py_modules=["ccc_main"],
    install_requires=[
        "click>=8.0",
        "rich>=10.0",
        "pydantic>=2.0",
        "requests>=2.25.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "ccc=ccc_main:main",
            "cccmd=ccc_main:main",
        ],
    },
    author="Collective Context Team",
    author_email="team@collective-context.org",
    description="Collective Context Commander - Multi-Agent AI Orchestration Tool",
    url="https://collective-context.org",
    python_requires=">=3.8",
)