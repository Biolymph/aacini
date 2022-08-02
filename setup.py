import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, "aacini", "__version__.py")) as f:
    exec(f.read(), about)

# Requirements
requirements = [
    "click==8.1.3",
    "pandas==1.4.3",
    "pysam==0.19.1"
]

setup(
    name="aacini",
    version=about["__version__"],
    url="https://github.com/Biolymph/minerva",
    author="Rosario Silva Sepulveda & Hassan Foroughi Asl",
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        "console_scripts": ["aacini=aacini.commands.base:cli"],
    },
)