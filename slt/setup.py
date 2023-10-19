from setuptools import setup, find_packages

setup(
    name='slt',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'slt = slt:main',
        ],
    },
    install_requires=["colorlog"],
)
