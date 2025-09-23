from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="drawtree",
    version="1.1.0",
    author="Game Tree Drawing Project",
    description="Generate TikZ code for game trees from extensive form (.ef) files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov"],
        "jupyter": ["jupyter", "jupyter-tikz"],
    },
    entry_points={
        "console_scripts": [
            "drawtree=drawtree.cli:main",
        ],
    },
    package_data={
        "drawtree": ["data/*.tex"],
    },
    include_package_data=True,
)