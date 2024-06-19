# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='streamdepletr',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'shapely',
        'geopandas',
    ],
    author='lijing',
    author_email='1076031338@qq.com',
    description='A package for modeling streamflow depletion using analytical models',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/fanlijing/streamdepletr.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Hydrology'
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
