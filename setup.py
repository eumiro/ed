"""
ed setup.py
"""
import re
from pathlib import Path

from setuptools import find_packages, setup

NAME = "ed"
KEYWORDS = [
    "ed",
    "editor",
    "text editor",
    "unix",
    "ed(1)",
    "the standard text editor",
]
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Telecommunications Industry",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Text Editors",
    "Topic :: Text Editors :: Text Processing",
    "Topic :: Utilities",
]
INSTALL_REQUIRES = []

# --+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----


if __name__ == "__main__":
    HERE = Path(__file__).resolve().parent
    META_FILE = (HERE / "src" / NAME / "__init__.py").read_text()
    META = dict(
        re.findall(r"^__(\w+)__ = ['\"]([^'\"]*)['\"]", META_FILE, re.M)
    )
    setup(
        name=NAME,
        description=META["description"],
        license=META["license"],
        url=META["url"],
        version=META["version"],
        author=META["author"],
        author_email=META["email"],
        maintainer=META["author"],
        maintainer_email=META["email"],
        keywords=KEYWORDS,
        long_description=Path("README.rst").read_text(),
        long_description_content_type="text/x-rst",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        extras_require={"test": ["pytest", "pre-commit"]},
        options={},
        include_package_data=True,
        entry_points={},
    )
