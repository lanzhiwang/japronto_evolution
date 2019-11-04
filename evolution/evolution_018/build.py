import argparse
import distutils
from distutils.command.build_ext import build_ext, CompileError
from distutils.core import Distribution
from glob import glob
import os.path
import shutil
from importlib import import_module
import os
import sys


class BuildSystem:
    def __init__(self, args):
        self.args = args
        # args: Namespace(debug=False, enable_reaper=True, path=None, profile_generate=False, profile_use=False)

    def get_extension_by_path(self, path):
        # print('path: {}'.format(path))  # path: pipeline/cpipeline_ext.py
        # print('os.path.splitext(path): {}'.format(os.path.splitext(path)))  # os.path.splitext(path): ('pipeline/cpipeline_ext', '.py')
        module_import = os.path.splitext(path)[0].replace('/', '.')
        # print('module_import: {}'.format(module_import))  # module_import: pipeline.cpipeline_ext

        module = import_module(module_import)
        # print('module: {}'.format(module))
        # module: <module 'pipeline.cpipeline_ext' from '/root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline_ext.py'>

        module.system = self
        extension = module.get_extension()
        # print('extension: {}'.format(extension))
        # extension: <distutils.extension.Extension('pipeline.cpipeline') at 0x7f3c24235e80>

        base_path = os.path.dirname(path)
        # print('base_path: {}'.format(base_path))  # base_path: pipeline

        def fix_path(p):
            if os.path.isabs(p):
                return p

            return os.path.abspath(os.path.join(base_path, p))

        for attr in ['sources', 'include_dirs', 'library_dirs', 'runtime_library_dirs']:
            val = getattr(extension, attr)
            # print('attr: {} val: {}'.format(attr, val))
            """
            attr: sources val: ['cpipeline.c']
            attr: include_dirs val: []
            attr: library_dirs val: []
            attr: runtime_library_dirs val: []
            """

            if not val:
                continue

            val = [fix_path(v) for v in val]
            # print('val: {}'.format(val))  # val: ['/root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.c']
            if attr == 'runtime_library_dirs':
                setattr(extension, attr, None)
                attr = 'extra_link_args'
                val = ['-Wl,-rpath,' + v for v in val]
                val = (getattr(extension, attr) or []) + val
            setattr(extension, attr, val)

        return extension

    def discover_extensions(self):
        self.extensions = []

        ext_files = glob('**/*_ext.py', recursive=True)
        # print('ext_files: {}'.format(ext_files))
        """
        ext_files: 
        [
        'pipeline/cpipeline_ext.py', 
        'response/cresponse_ext.py', 
        'protocol/cprotocol_ext.py', 
        'parser/cparser_ext.py', 
        'request/crequest_ext.py', 
        'router/cmatcher_ext.py'
        ]
        """
        self.extensions = [self.get_extension_by_path(f) for f in ext_files]

        return self.extensions


def dest_folder(mod_name):
    return '/'.join(mod_name.split('.')[:-1])


def prune():
    paths = glob('build/**/*.o', recursive=True)
    paths.extend(glob('build/**/*.so', recursive=True))
    for path in paths:
        os.remove(path)


def main():
    argparser = argparse.ArgumentParser('build')
    argparser.add_argument(
        '-d', dest='debug', const=True, action='store_const', default=False)
    argparser.add_argument(
        '--profile-generate', dest='profile_generate', const=True,
        action='store_const', default=False)
    argparser.add_argument(
        '--profile-use', dest='profile_use', const=True,
        action='store_const', default=False)
    argparser.add_argument(
        '--disable-reaper', dest='enable_reaper', const=False,
        action='store_const', default=True)
    argparser.add_argument('--path', dest='path')
    args = argparser.parse_args(sys.argv[1:])

    distutils.log.set_verbosity(1)

    # print('args: {}'.format(args))
    # args: Namespace(debug=False, enable_reaper=True, path=None, profile_generate=False, profile_use=False)
    system = BuildSystem(args)

    if args.path:
        ext_modules = [system.get_extension_by_path(args.path)]
    else:
        ext_modules = system.discover_extensions()
    # print('ext_modules: {}'.format(ext_modules))
    """
    ext_modules: 
    [
    <distutils.extension.Extension('pipeline.cpipeline') at 0x7f0d2bdd8d30>, 
    <distutils.extension.Extension('response.cresponse') at 0x7f0d2bdd8da0>, 
    <distutils.extension.Extension('protocol.cprotocol') at 0x7f0d2b976c88>, 
    <distutils.extension.Extension('parser.cparser') at 0x7f0d2bdd8f28>, 
    <distutils.extension.Extension('request.crequest') at 0x7f0d2bdd8eb8>, 
    <distutils.extension.Extension('router.cmatcher') at 0x7f0d2b976cf8>
    ]
    """

    dist = Distribution(dict(ext_modules=ext_modules))
    # print('dist: {}'.format(dist))  # dist: <distutils.dist.Distribution object at 0x7f25982d3d30>

    def append_args(arg_name, values):
        for ext_module in ext_modules:
            arg_value = getattr(ext_module, arg_name) or []
            arg_value.extend(values)
            setattr(ext_module, arg_name, arg_value)

    def append_compile_args(*values):
        append_args('extra_compile_args', values)

    def append_link_args(*values):
        append_args('extra_link_args', values)


    append_compile_args('-frecord-gcc-switches')
    append_compile_args('-std=c99')

    if args.debug:
        append_compile_args('-g', '-O0')
    if args.profile_generate:
        append_compile_args('--profile-generate')
        append_link_args('-lgcov')
    if args.profile_use:
        for ext_module in ext_modules:
            if ext_module.name == 'parser.cparser':
                continue
            ext_module.extra_compile_args.append('--profile-use')


    prune()

    cmd = build_ext(dist)
    cmd.finalize_options()

    try:
        cmd.run()
    except CompileError:
        sys.exit(1)

    for ext_module in ext_modules:
        shutil.copy(
            cmd.get_ext_fullpath(ext_module.name),
            dest_folder(ext_module.name))


if __name__ == '__main__':
    main()

"""
(venv) [root@huzhi-code picohttpparser]# bash build
+ gcc -c picohttpparser.c -O3 -fpic -msse4.2
+ gcc -shared -o libpicohttpparser.so picohttpparser.o
+ strip libpicohttpparser.so
(venv) [root@huzhi-code picohttpparser]#
(venv) [root@huzhi-code picohttpparser]# cd ..
(venv) [root@huzhi-code evolution_018]#
(venv) [root@huzhi-code evolution_018]# python3 build.py
building 'pipeline.cpipeline' extension
creating build
creating build/temp.linux-x86_64-3.6
creating build/temp.linux-x86_64-3.6/root
creating build/temp.linux-x86_64-3.6/root/work
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/pipeline
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DPIPELINE_OPAQUE=1 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.o -frecord-gcc-switches -std=c99
creating build/lib.linux-x86_64-3.6
creating build/lib.linux-x86_64-3.6/pipeline
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.o -L/usr/lib64 -lpython3.6m -o build/lib.linux-x86_64-3.6/pipeline/cpipeline.cpython-36m-x86_64-linux-gnu.so

gcc -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c cpipeline.c -o cpipeline.o
gcc cpipeline.o -L/usr/lib64 -lpython3.6m -o cpipeline.cpython-36m-x86_64-linux-gnu.so



building 'response.cresponse' extension
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/response
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/response/cresponse.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/response/cresponse.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/capsule.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -frecord-gcc-switches -std=c99
creating build/lib.linux-x86_64-3.6/response
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/response/cresponse.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -L/usr/lib64 -lpython3.6m -o build/lib.linux-x86_64-3.6/response/cresponse.cpython-36m-x86_64-linux-gnu.so

gcc -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c cresponse.c -o cresponse.o
gcc -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c capsule.c -o capsule.o
gcc cresponse.o capsule.o -L/usr/lib64 -lpython3.6m -o cresponse.cpython-36m-x86_64-linux-gnu.so



building 'protocol.cprotocol' extension
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/protocol
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/parser
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DREAPER_ENABLED=1 -I/root/work/japronto_evolution/evolution/evolution_018/protocol -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/evolution/evolution_018/parser -I/root/work/japronto_evolution/evolution/evolution_018/pipeline -I/root/work/japronto_evolution/evolution/evolution_018/router -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018/response -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/protocol/cprotocol.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/protocol/cprotocol.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DREAPER_ENABLED=1 -I/root/work/japronto_evolution/evolution/evolution_018/protocol -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/evolution/evolution_018/parser -I/root/work/japronto_evolution/evolution/evolution_018/pipeline -I/root/work/japronto_evolution/evolution/evolution_018/router -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018/response -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/capsule.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DREAPER_ENABLED=1 -I/root/work/japronto_evolution/evolution/evolution_018/protocol -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/evolution/evolution_018/parser -I/root/work/japronto_evolution/evolution/evolution_018/pipeline -I/root/work/japronto_evolution/evolution/evolution_018/router -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018/response -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/parser/cparser.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/parser/cparser.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DREAPER_ENABLED=1 -I/root/work/japronto_evolution/evolution/evolution_018/protocol -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/evolution/evolution_018/parser -I/root/work/japronto_evolution/evolution/evolution_018/pipeline -I/root/work/japronto_evolution/evolution/evolution_018/router -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018/response -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.o -frecord-gcc-switches -std=c99
creating build/lib.linux-x86_64-3.6/protocol
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/protocol/cprotocol.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/parser/cparser.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/pipeline/cpipeline.o -L/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -L/usr/lib64 -lpicohttpparser -lpython3.6m -o build/lib.linux-x86_64-3.6/protocol/cprotocol.cpython-36m-x86_64-linux-gnu.so -Wl,-rpath,/root/work/japronto_evolution/evolution/evolution_018/picohttpparser



gcc
-I/root/work/japronto_evolution/evolution/evolution_018/protocol 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/evolution/evolution_018/parser 
-I/root/work/japronto_evolution/evolution/evolution_018/pipeline 
-I/root/work/japronto_evolution/evolution/evolution_018/router 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018/response 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c cprotocol.c -o cprotocol.o

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/protocol 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/evolution/evolution_018/parser 
-I/root/work/japronto_evolution/evolution/evolution_018/pipeline 
-I/root/work/japronto_evolution/evolution/evolution_018/router 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018/response 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c capsule.c -o capsule.o

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/protocol 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/evolution/evolution_018/parser 
-I/root/work/japronto_evolution/evolution/evolution_018/pipeline 
-I/root/work/japronto_evolution/evolution/evolution_018/router 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018/response 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c cparser.c -o cparser.o

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/protocol 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/evolution/evolution_018/parser 
-I/root/work/japronto_evolution/evolution/evolution_018/pipeline 
-I/root/work/japronto_evolution/evolution/evolution_018/router 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018/response 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c cpipeline.c -o cpipeline.o

gcc 
cprotocol.o 
capsule.o 
cparser.o 
cpipeline.o 
-L/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-L/usr/lib64 
-lpicohttpparser 
-lpython3.6m -o cprotocol.cpython-36m-x86_64-linux-gnu.so 



building 'parser.cparser' extension
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DPARSER_STANDALONE=1 -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/parser/cparser.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/parser/cparser.o -frecord-gcc-switches -std=c99
creating build/lib.linux-x86_64-3.6/parser
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/parser/cparser.o -L/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -L/usr/lib64 -lpicohttpparser -lpython3.6m -o build/lib.linux-x86_64-3.6/parser/cparser.cpython-36m-x86_64-linux-gnu.so -Wl,-rpath,/root/work/japronto_evolution/evolution/evolution_018/picohttpparser



gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -DPARSER_STANDALONE=1 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c cparser.c -o cparser.o

gcc cparser.o 
-L/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-L/usr/lib64 
-lpicohttpparser 
-lpython3.6m -o cparser.cpython-36m-x86_64-linux-gnu.so



building 'request.crequest' extension
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/request
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/evolution/evolution_018/response -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/request/crequest.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/request/crequest.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/evolution/evolution_018/response -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/capsule.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -frecord-gcc-switches -std=c99
creating build/lib.linux-x86_64-3.6/request
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/request/crequest.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -L/usr/lib64 -lpython3.6m -o build/lib.linux-x86_64-3.6/request/crequest.cpython-36m-x86_64-linux-gnu.so

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/evolution/evolution_018/response 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c crequest.c -o crequest.o

gcc 
-pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC 
-I/root/work/japronto_evolution/evolution/evolution_018/picohttpparser 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/evolution/evolution_018/response 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c capsule.c -o capsule.o

gcc crequest.o capsule.o -L/usr/lib64 -lpython3.6m -o crequest.cpython-36m-x86_64-linux-gnu.so



building 'router.cmatcher' extension
creating build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/router
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/router/cmatcher.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/router/cmatcher.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/router/match_dict.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/router/match_dict.o -frecord-gcc-switches -std=c99
gcc -pthread -Wno-unused-result -Wsign-compare -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fwrapv -fPIC -I/root/work/japronto_evolution/evolution/evolution_018/request -I/root/work/japronto_evolution/evolution/evolution_018 -I/root/work/japronto_evolution/venv/include -I/usr/include/python3.6m -c /root/work/japronto_evolution/evolution/evolution_018/capsule.c -o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -frecord-gcc-switches -std=c99
creating build/lib.linux-x86_64-3.6/router
gcc -pthread -shared -Wl,-z,relro -g build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/router/cmatcher.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/router/match_dict.o build/temp.linux-x86_64-3.6/root/work/japronto_evolution/evolution/evolution_018/capsule.o -L/usr/lib64 -lpython3.6m -o build/lib.linux-x86_64-3.6/router/cmatcher.cpython-36m-x86_64-linux-gnu.so

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m 
-c cmatcher.c -o cmatcher.o

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m -c match_dict.c -o match_dict.o

gcc 
-I/root/work/japronto_evolution/evolution/evolution_018/request 
-I/root/work/japronto_evolution/evolution/evolution_018 
-I/root/work/japronto_evolution/venv/include 
-I/usr/include/python3.6m -c capsule.c -o capsule.o

gcc cmatcher.o match_dict.o capsule.o -L/usr/lib64 -lpython3.6m -o cmatcher.cpython-36m-x86_64-linux-gnu.so



(venv) [root@huzhi-code evolution_018]#
"""