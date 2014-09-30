# Copyright (C) 2014 Tragnarion Studios
#
# UE4 project creator.
#
# Author: Moritz Wundke

from setuptools import setup, find_packages

setup(
    name = 'ue4_copyproject',
    version = '0.1',
    description = 'UE4 project creator',
    author = 'Moritz Wundke',
    packages = find_packages(),
    zip_safe = False,
)