from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='hardback',
    version='0.2',
    packages=find_packages(),
    entry_points={
    'console_scripts': [
    'hardback = hardback.main:main'
    ]
    },
    zip_safe=True,

    author='Allan Saddi',
    author_email='allan@saddi.com',
    description='Hardcopy backup utility'
    )

    
