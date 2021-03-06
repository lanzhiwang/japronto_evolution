from distutils.core import setup, Extension

import os.path

shared_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'picohttpparser'))

impl_cext = Extension(
    'impl_cext', sources=['impl_cext.c'],
    libraries=['picohttpparser'], include_dirs=[shared_path],
    library_dirs=[shared_path], extra_link_args=['-Wl,-rpath,' + shared_path])

setup(
    name='cpyextphp', version='1.0', description='Parse request',
    ext_modules=[impl_cext])
