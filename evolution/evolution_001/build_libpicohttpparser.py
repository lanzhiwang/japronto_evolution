import os.path

import cffi
ffibuilder = cffi.FFI()

shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'picohttpparser'))
# /root/work/japronto_evolution/evolution/evolution_001/picohttpparser

ffibuilder.set_source("libpicohttpparser",
                      """
                      #include "picohttpparser.h"
                      """,
                      libraries=['picohttpparser'],
                      include_dirs=[shared_path],
                      library_dirs=[shared_path],
                      extra_link_args=['-Wl,-rpath=' + shared_path])

ffibuilder.cdef("""
    struct phr_header {
        const char *name;
        size_t name_len;
        const char *value;
        size_t value_len;
    };

    int phr_parse_request(const char *buf, size_t len, const char **method, size_t *method_len, const char **path, size_t *path_len,
                          int *minor_version, struct phr_header *headers, size_t *num_headers, size_t last_len);
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
