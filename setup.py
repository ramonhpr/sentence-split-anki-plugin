import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="language word separator",
    version="1.0.0",
    author="Ramon Ribeiro",
    author_email="rhpr1509@gmail.com",
    description=("Anki add-on to separate words from phrases in any language"),
    license="MIT",
    keywords="Anki Add-on",
    url="https://github.com/ramonhpr/word-separator",
    install_requires=['googletrans', 'gtts', 'jisho_api', 'pykakasi'],
    packages=['packages'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)