from setuptools import setup, find_packages

setup(
    name='gx-mcp-server',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastmcp>=2.8', 'fastapi', 'uvicorn',
        'pandas', 'great_expectations', 'requests'
    ],
    extras_require={'dev': ['pytest', 'pre-commit', 'black', 'isort']},
)
