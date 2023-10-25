from setuptools import setup, find_packages

setup(
    name='sltools',
    version='0.1.2',
    description='S.T.A.L.K.E.R Localization Toolbox',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='HalavicH',
    author_email='HalavicH@gmail.com',
    url='https://github.com/HalavicH/stalker-localization-toolbox',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='XML S.T.A.L.K.E.R stalker mods modding game tools translate analysis',
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
        "GitPython~=3.1.40",
        "setuptools~=68.2.2"
    ],
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/HalavicH/stalker-localization-toolbox/issues/',
        'Source': 'https://github.com/HalavicH/stalker-localization-toolbox/',
        'Documentation': 'https://github.com/HalavicH/stalker-localization-toolbox/wiki',
    },
)
