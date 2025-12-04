from pathlib import Path
from setuptools import setup, find_packages

README = Path(__file__).with_name("README.md")
long_description = README.read_text(encoding="utf-8") if README.exists() else ""

setup(
    name="focuspro",
    version="1.0.0",
    description="A productivity and planning toolkit for students.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Inaara, Thomas, Anita",
    author_email="team@example.com",
    packages=find_packages(),
    py_modules=["run_demo"],
    install_requires=[],
    extras_require={"dev": ["pytest"]},
    python_requires=">=3.9",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "focuspro-demo=run_demo:main",
        ]
    },
)
