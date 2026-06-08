import os
from setuptools import find_packages
from setuptools import setup
import re


VERSIONFILE=os.path.join('src', '_version.py')
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else: 
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(name='traitar2',
        version = verstr,
        description='Traitar2 - Improved microbial trait analyzer (fork of original Traitar)',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/GenomicaMicrob/traitar2',
        author='Aaron Weimann',
        author_email='weimann@hhu.de',
        maintainer='Bruno Gomez-Gil, Microbial Genomics Lab, CIAD AC',
        maintainer_email='bruno@ciad.mx',
        license='GNU General Public License, version 3 (GPL-3.0)',
        packages= find_packages(),
        include_package_data = True,
        scripts = ['bin/traitar2'],
        zip_safe=False,
        install_requires = ["pandas >= 0.13.1", "matplotlib >= 1.3.1", "numpy >= 1.6", "scipy >= 0.13.3"])
