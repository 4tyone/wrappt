from setuptools import setup, find_packages

setup(
    name="wrappt",
    version="0.1.0",
    description="Lightweight and modular LLM wrapper framework.",
    author="Mels Hakobyan",
    author_email="mels@4tyone.com",
    url="https://github.com/4tyone/wrappt",
    packages=find_packages(
        where=".",
        exclude=[
            "wrappt_env",
            "wrappt_env.*",
            "exe",
            "exe.*"
            "*.pyc",
            "*.pyo",
            "__pycache__",
            "tests",
            "*.md",
            "*.txt",
            "__init__.py"
            ]
    ),
    python_requires=">=3.10",
    install_requires=[
        "pydantic==2.10.3",
        "instructor==1.7.0",
        "anthropic==0.40.0",
        "openai==1.57.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            # Define CLI commands here if needed
            # "wrappt-cli = wrappt.cli:main",
        ],
    },
)