from setuptools import setup, find_packages
from pathlib import Path
file_path = Path(__file__).parent.resolve()
def get_version():
    version_path = file_path.joinpath('OpenCtrl','__init__.py')
    with open(version_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and\
                    not line.startswith('#')]
try:
    with open(file_path.joinpath('Readme.md'), 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    raise RuntimeError("Readme.md file not found")
setup(
    name='OpenCtrl',
    version=get_version(),
    author='Shoham Roy',
    author_email='shohamc3@gmail.com',
    description='A library for Optimal Control and System Dynamics',
    url='https://github.com/shoham-roy31/OpenCtrl',
    project_urls={
        'Bug Tracker':'https://github.com/shoham-roy31/OpenCtrl/issues',
        'Source Code':'https://github.com/shoham-roy31/OpenCtrl',
    },
    packages=find_packages(exclude=['test*','tests.*','test*.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Control Systems',
        'Topic :: Atrificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.18.0',
    ],
    extras_require={
        'dev': [
            'pytest>=8'
        ]
    },
    include_package_data=True,
    zip_safe=False,
)