import subprocess

import parsers
import cases


def get_http10long():
    return cases.base['10long'].data


def get_websites(size=2 ** 19):
    data = b''
    while len(data) < size:
        for c in cases.websites.values():
            data += c.data

    return data


if __name__ == '__main__':
    setup = """
import parsers
import do_perf
parser, *_ = parsers.make_{}(lambda: parsers.silent_callback)
data = do_perf.get_{}()
"""

    loop = """
parser.feed(data)
parser.feed_disconnect()
"""

    for dataset in ['http10long', 'websites']:
        for parser in ['cffi', 'cext']:
            print('-- {} {} --'.format(dataset, parser))
            print([
                'python', '-m', 'perf', 'timeit', '-s', setup.format(parser, dataset), loop])
            subprocess.check_call([
                'python', '-m', 'perf', 'timeit', '-s', setup.format(parser, dataset), loop])
            print()

"""
-- http10long cffi --
['python', '-m', 'perf', 'timeit', '-s', '\nimport parsers\nimport do_perf\nparser, *_ = parsers.make_cffi(lambda: parsers.silent_callback)\ndata = do_perf.get_http10long()\n', '\nparser.feed(data)\nparser.feed_disconnect()\n']

-- http10long cext --
['python', '-m', 'perf', 'timeit', '-s', '\nimport parsers\nimport do_perf\nparser, *_ = parsers.make_cext(lambda: parsers.silent_callback)\ndata = do_perf.get_http10long()\n', '\nparser.feed(data)\nparser.feed_disconnect()\n']

-- websites cffi --
['python', '-m', 'perf', 'timeit', '-s', '\nimport parsers\nimport do_perf\nparser, *_ = parsers.make_cffi(lambda: parsers.silent_callback)\ndata = do_perf.get_websites()\n', '\nparser.feed(data)\nparser.feed_disconnect()\n']

-- websites cext --
['python', '-m', 'perf', 'timeit', '-s', '\nimport parsers\nimport do_perf\nparser, *_ = parsers.make_cext(lambda: parsers.silent_callback)\ndata = do_perf.get_websites()\n', '\nparser.feed(data)\nparser.feed_disconnect()\n']

python -m perf timeit -s
import parsers
import do_perf
parser, *_ = parsers.make_cext(lambda: parsers.silent_callback)
data = do_perf.get_websites()
parser.feed(data)
parser.feed_disconnect()

"""