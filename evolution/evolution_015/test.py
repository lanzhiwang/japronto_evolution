from functools import partial
from unittest.mock import Mock

import pytest


from cases import base, parametrize_cases
from parts import one_part, make_parts, geometric_series, fancy_series
import parsers


def make_part_functions():
    return [
        one_part,
        partial(make_parts, get_size=15),
        partial(make_parts, get_size=geometric_series()),
        partial(make_parts, get_size=geometric_series(), dir=-1),
        partial(make_parts, get_size=fancy_series())
    ]


@pytest.mark.parametrize('data,get_size,dir,parts',
[
    (b'abcde', 2, 1, [b'ab', b'cd', b'e']),
    (b'abcde', 2, -1, [b'a', b'bc', b'de']),
    (b'aaBBBBccccCCCCd', geometric_series(), 1,
     [b'aa', b'BBBB', b'ccccCCCC', b'd']),
    (b'dCCCCccccBBBBaa', geometric_series(), -1,
     [b'd', b'CCCCcccc', b'BBBB', b'aa'])
])
def test_make_parts(data, get_size, dir, parts):
    assert make_parts(data, get_size, dir) == parts


def parametrize_make_parser():
    ids = []
    factories = []
    if hasattr(parsers, 'make_cext'):
        factories.append(partial(parsers.make_cext, Mock))
        ids.append('cext')

    factories.append(partial(parsers.make_cffi, Mock))
    ids.append('cffi')

    return pytest.mark.parametrize('make_parser', factories, ids=ids)


@pytest.mark.parametrize('do_parts', make_part_functions())
@parametrize_cases(
    'base',
    '10long', '10short', '10long+10short', '10short+10long',

    '10malformed_headers1', '10malformed_headers2', '10incomplete_headers',
    '10long+10malformed_headers2', '10long+10incomplete_headers',
    '10short+10malformed_headers1', '10short+10malformed_headers2')
@parametrize_make_parser()
def test_http10(make_parser, do_parts, cases):
    parser, on_headers, on_error, on_body = make_parser()
    for i, case in enumerate(cases, 1):
        parts = do_parts(case.data)

        for part in parts:
            parser.feed(part)
        parser.feed_disconnect()

        header_errors = 1 if case.error and 'headers' in case.error else 0
        body_errors = 1 if case.error and 'body' in case.error else 0

        assert on_headers.call_count == i - header_errors
        assert on_error.call_count == header_errors + body_errors
        assert on_body.call_count == i - header_errors - body_errors

        if on_error.called:
            assert on_error.call_args[0][0] == case.error

        if header_errors:
            continue

        request = on_headers.call_args[0][0]

        assert request.method == case.method
        assert request.path == case.path
        assert request.version == case.version
        assert request.headers == case.headers

        if body_errors:
            continue

        assert request.body == case.body


@parametrize_make_parser()
def test_empty(make_parser):
    parser, on_headers, on_error, on_body = make_parser()

    parser.feed_disconnect()
    parser.feed(b'')
    parser.feed(b'')
    parser.feed_disconnect()
    parser.feed_disconnect()
    parser.feed(b'')

    assert not on_headers.called
    assert not on_error.called
    assert not on_body.called


@pytest.mark.parametrize('do_parts', make_part_functions())
@parametrize_cases(
    'base',
    '11get', '11clget', '11clkeep', '11clzero', '11clclose',
    '11clkeep+11clclose', '11clkeep+11clkeep',
    '11clclose+11clkeep', '11clclose+11clclose',
    '11get+11clclose', '11clkeep+11get', '11clget+11get',
    '11clclose+11clclose+11clkeep',
    '11clkeep+11clclose+11clkeep',
    '11clclose+11clzero+11clkeep',
    '11clzero+11clclose+11clzero',
    '11clkeep+11get+11clzero',
    '11clzero+11clzero',
    '11get+11clget+11get',

    '11clincomplete_headers', '11clincomplete_body',
    '11clinvalid1', '11clinvalid2', '11clinvalid3',
    '11clinvalid4', '11clinvalid5',
    '11clkeep+11clincomplete_headers', '11clkeep+11clincomplete_body',
    '11clzero+11clincomplete_headers', '11clzero+11clincomplete_body',
    '11clclose+11clkeep+11clincomplete_body',
    '11get+11clincomplete_body',
    '11clget+11clincomplete_headers'
)
@parametrize_make_parser()
def test_http11_contentlength(make_parser, do_parts, cases):
    parser, on_headers, on_error, on_body = make_parser()

    data = b''.join(c.data for c in cases)
    parts = do_parts(data)

    for part in parts:
        parser.feed(part)
    parser.feed_disconnect()

    header_count = 0
    error_count = 0
    body_count = 0

    for i, case in enumerate(cases):
        if case.error and 'headers' in case.error:
            error_count += 1
            continue

        header_count += 1
        request = on_headers.call_args_list[i][0][0]

        assert request.method == case.method
        assert request.path == case.path
        assert request.version == case.version
        assert request.headers == case.headers

        if case.error and 'body' in case.error:
            error_count += 1
            continue

        body_count += 1

        assert request.body == case.body

    assert on_headers.call_count == header_count
    assert on_error.call_count == error_count
    assert on_body.call_count == body_count


@pytest.mark.parametrize('do_parts', make_part_functions())
@parametrize_cases(
    'base',
    '11chunked1', '11chunked2', '11chunked3', '11chunkedzero',
    '11chunked1+11chunked1',
    '11chunked1+11chunked2',
    '11chunked2+11chunked1',
    '11chunked2+11chunked3',
    '11chunked1+11chunked2+11chunked3',
    '11chunked3+11chunked2+11chunked1',
    '11chunked3+11chunked3+11chunked3',

    '11chunkedincomplete_body', '11chunkedmalformed_body',
    '11chunked1+11chunkedincomplete_body',
    '11chunked1+11chunkedmalformed_body',
    '11chunked2+11chunkedincomplete_body',
    '11chunked2+11chunkedmalformed_body',
    '11chunked2+11chunked2+11chunkedincomplete_body',
    '11chunked3+11chunked1+11chunkedmalformed_body'
)
@parametrize_make_parser()
def test_http11_chunked(make_parser, do_parts, cases):
    parser, on_headers, on_error, on_body = make_parser()
    data = b''.join(c.data for c in cases)
    parts = do_parts(data)

    for part in parts:
        parser.feed(part)
        if on_error.called:
            break
    parser.feed_disconnect()

    header_count = 0
    error_count = 0
    body_count = 0

    for i, case in enumerate(cases):
        if case.error and 'headers' in case.error:
            error_count += 1
            continue

        header_count += 1
        request = on_headers.call_args_list[i][0][0]

        assert request.method == case.method
        assert request.path == case.path
        assert request.version == case.version
        assert request.headers == case.headers

        if case.error and 'body' in case.error:
            error_count += 1
            continue

        body_count += 1

        assert request.body == case.body

    assert on_headers.call_count == header_count
    assert on_error.call_count == error_count
    assert on_body.call_count == body_count


@pytest.mark.parametrize('do_parts', make_part_functions())
@parametrize_cases(
    'base',
    '11chunked1+11clzero',
    '11clkeep+11chunked2',
    '11chunked2+11clclose',
    '11clzero+11chunked3',
    '11clclose+11chunked1+11chunked3',
    '11chunked3+11clkeep+11clclose',
    '11chunked3+11chunked3+11clclose'
)
@parametrize_make_parser()
def test_http11_mixed(make_parser, do_parts, cases):
    parser, on_headers, on_error, on_body = make_parser()
    data = b''.join(c.data for c in cases)
    parts = do_parts(data)

    for part in parts:
        parser.feed(part)
    parser.feed_disconnect()

    assert on_headers.call_count == len(cases)
    assert not on_error.called
    assert on_body.call_count == len(cases)

    for i, case in enumerate(cases):
        request = on_headers.call_args_list[i][0][0]

        assert request.method == case.method
        assert request.path == case.path
        assert request.version == case.version
        assert request.headers == case.headers
        assert request.body == case.body
