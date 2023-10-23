from setuptools import setup, find_packages

setup(
    name='sltools',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sltools = src.slt:main',
        ],
    },
    install_requires=[
        "colorama~=0.4.6",
        "chardet~=3.0.4",
        "argparse~=1.4.0",
        "colorlog~=6.7.0",
        "requests~=2.31.0",
        "lxml~=4.9.3",
        "langdetect~=1.0.9",
        "prettytable~=3.9.0",
        "rich~=13.5.3",
        "rich_argparse~=1.4.0",
    ],
)
