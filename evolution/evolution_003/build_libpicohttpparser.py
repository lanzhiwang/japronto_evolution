# -*- coding: utf-8 -*-

"""
picohttpparser 是用 C 语言写的解析 HTTP 协议的库
使用方法一：
1、编译 picohttpparser
2、使用 python 的 CFFI 库封装 picohttpparser
3、编译成 Python 模块 libpicohttpparser

使用方法二：
1、直接使用 Python.h 直接调用 picohttpparser
2、编译成 Python 模块 impl_cext
"""

import os.path

import cffi
ffibuilder = cffi.FFI()

shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'picohttpparser'))


ffibuilder.set_source("libpicohttpparser", """
   #include "picohttpparser.h"
   """, libraries=['picohttpparser'], include_dirs=[shared_path], library_dirs=[shared_path],
#   extra_objects=[os.path.join(shared_path, 'picohttpparser.o')],
   extra_link_args=['-Wl,-rpath=' + shared_path])   # or a list of libraries to link with
    # (more arguments like setup.py's Extension class:
    # include_dirs=[..], extra_objects=[..], and so on)

ffibuilder.cdef("""
    struct phr_header {
        const char *name;
        size_t name_len;
        const char *value;
        size_t value_len;
    };

    struct phr_chunked_decoder {
        size_t bytes_left_in_chunk; /* number of bytes left in current chunk */
        char consume_trailer;       /* if trailing headers should be consumed */
        char _hex_count;
        char _state;
    };

    int phr_parse_request(const char *buf, size_t len, const char **method, size_t *method_len, const char **path, size_t *path_len,
                          int *minor_version, struct phr_header *headers, size_t *num_headers, size_t last_len);

    ssize_t phr_decode_chunked(struct phr_chunked_decoder *decoder, char *buf, size_t *bufsz);
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)

"""
(venv) [root@huzhi-code picohttpparser]# bash build
+ gcc -c picohttpparser.c -O3 -fPIC -msse4.2 -o ssepicohttpparser.o
+ gcc -c picohttpparser.c -O3 -fPIC -o picohttpparser.o
+ gcc -fPIC -shared -o libpicohttpparser.so picohttpparser.o ssepicohttpparser.o
(venv) [root@huzhi-code picohttpparser]#

#	picohttpparser/libpicohttpparser.so
#	picohttpparser/picohttpparser.o
#	picohttpparser/ssepicohttpparser.o

(venv) [root@huzhi-code evolution_003]#


(venv) [root@huzhi-code evolution_003]# python3 build_libpicohttpparser.py
generating ./libpicohttpparser.c
the current directory is '/root/work/japronto_evolution/evolution/evolution_003'
running build_ext
building 'libpicohttpparser' extension
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_003/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c libpicohttpparser.c -o ./libpicohttpparser.o
gcc -pthread -shared -Wl,-z,relro -g ./libpicohttpparser.o -L/root/work/japronto_evolution/evolution/evolution_003/picohttpparser -L/usr/lib64 -lpicohttpparser -lpython3.6m -o ./libpicohttpparser.cpython-36m-x86_64-linux-gnu.so -Wl,-rpath=/root/work/japronto_evolution/evolution/evolution_003/picohttpparser
(venv) [root@huzhi-code evolution_003]#

#	libpicohttpparser.c
#	libpicohttpparser.cpython-36m-x86_64-linux-gnu.so
#	libpicohttpparser.o

(venv) [root@huzhi-code evolution_003]#

"""