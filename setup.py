from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="dbt-col",
    version="0.1.0",
    author="dbt-col Team",
    author_email="your-email@example.com",
    description="Automated dbt to OpenMetadata publisher - no user intervention required",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dbt-col",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openmetadata-ingestion>=1.2.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "dbt-col=dbt_col.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        'dbt_col': ['dbt_package/**/*'],
    },
) 