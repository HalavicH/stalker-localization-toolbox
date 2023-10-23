from setuptools import setup, find_packages

setup(
    name='sltools',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sltools = sltools.slt:main',
        ],
    },
    package_data={'sltools': ['./resources/logger-config.ini']},
    install_requires=["colorlog"],
)
