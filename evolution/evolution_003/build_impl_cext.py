from distutils.core import setup, Extension

import os.path

shared_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'picohttpparser'))

impl_cext = Extension(
    'impl_cext', sources=['impl_cext.c'],
    libraries=['picohttpparser'], include_dirs=[shared_path],
    library_dirs=[shared_path], extra_link_args=['-Wl,-rpath,' + shared_path], extra_compile_args=['-std=c99'])

setup(
    name='cpyextphp', version='1.0', description='Parse request',
    ext_modules=[impl_cext])



"""
(venv) [root@huzhi-code evolution_003]# bash build_impl_cext
+ python build_impl_cext.py build
running build
running build_ext
building 'impl_cext' extension
creating build
creating build/temp.linux-x86_64-3.6
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_003/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c impl_cext.c -o build/temp.linux-x86_64-3.6/impl_cext.o -std=c99
creating build/lib.linux-x86_64-3.6
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/impl_cext.o -L/root/work/japronto_evolution/evolution/evolution_003/picohttpparser -L/usr/lib64 -lpicohttpparser -lpython3.6m -o build/lib.linux-x86_64-3.6/impl_cext.cpython-36m-x86_64-linux-gnu.so -Wl,-rpath,/root/work/japronto_evolution/evolution/evolution_003/picohttpparser
+ cp build/lib.linux-x86_64-3.6/impl_cext.cpython-36m-x86_64-linux-gnu.so .
(venv) [root@huzhi-code evolution_003]#

#	build/
#	impl_cext.cpython-36m-x86_64-linux-gnu.so

(venv) [root@huzhi-code evolution_003]#
(venv) [root@huzhi-code evolution_003]# tree -a build
build
├── lib.linux-x86_64-3.6
│   └── impl_cext.cpython-36m-x86_64-linux-gnu.so
└── temp.linux-x86_64-3.6
    └── impl_cext.o

2 directories, 2 files
(venv) [root@huzhi-code evolution_003]#

"""
