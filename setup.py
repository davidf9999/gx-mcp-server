from pathlib import Path

from setuptools import find_packages, setup

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="gx-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    description="Expose Great Expectations data-quality checks via MCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "fastmcp>=2.8",
        "fastapi",
        "uvicorn",
        "pandas",
        "great_expectations",
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pre-commit",
            "black",
            "isort",
            "mypy",
            "types-requests",
            "pandas-stubs",
        ]
    },
)
