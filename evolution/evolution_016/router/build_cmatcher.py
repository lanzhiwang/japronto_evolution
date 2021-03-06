from distutils.core import setup, Extension

import os.path
import sys

cmatcher = Extension(
    'cmatcher', sources=['cmatcher.c'],
    libraries=[], include_dirs=[],
    library_dirs=[], extra_link_args=[],
    extra_compile_args=[])

setup(
    name='cmatcher', version='1.0', description='',
    ext_modules=[cmatcher])
