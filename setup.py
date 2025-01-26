import re
from setuptools import setup, find_packages


VERSION = '0.0.1'


with open("README.md", "r") as readme:
    description = readme.read()
    # Patch the relative links to absolute URLs that will work on PyPI.
    description2 = re.sub(
        r']\(([\w/.-]+\.png)\)',
        r'](https://github.com/vivarium-collective/multicell-schema/raw/main/\1)',
        description)
    long_description = re.sub(
        r']\(([\w/.-]+)\)',
        r'](https://github.com/vivarium-collective/multicell-schema/blob/main/\1)',
        description2)

setup(
    name="multicell-schema",
    version=VERSION,
    author="Eran Agmon",
    author_email="agmon.eran@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vivarium-collective/multicell-schema",
    # packages=find_packages(),
    packages=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        "jsonschema",
    ]
)
