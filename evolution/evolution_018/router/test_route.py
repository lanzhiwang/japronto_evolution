import pytest

from router.route import parse, MatcherEntry, Segment, SegmentType, Route, \
    compile


@pytest.mark.parametrize('pattern,result', [
    ('/', [('exact', '/')]),
    ('/{{a}}', [('exact', '/{a}')]),
    ('{a}', [('placeholder', 'a')]),
    ('a/{a}', [('exact', 'a/'), ('placeholder', 'a')]),
    ('{a}/a', [('placeholder', 'a'), ('exact', '/a')]),
    ('{a}/{{a}}', [('placeholder', 'a'), ('exact', '/{a}')]),
    ('{a}/{b}', [('placeholder', 'a'), ('exact', '/'), ('placeholder', 'b')])
])
def test_parse(pattern, result):
    assert parse(pattern) == result


@pytest.mark.parametrize('pattern,error', [
    ('{a', 'Unbalanced'),
    ('{a}/{b', 'Unbalanced'),
    ('{a}a', 'followed by'),
    ('{a}/{a}', 'Duplicate')
])
def test_parse_error(pattern, error):
    with pytest.raises(ValueError) as info:
        parse(pattern)
    assert error in info.value.args[0]


from collections import namedtuple

DecodedRoute = namedtuple(
    'DecodedRoute', 'route_id,handler_id,segments,methods')


def decompile(buffer):
    route_id, handler_id, pattern_len, methods_len \
        = MatcherEntry.unpack_from(buffer, 0)
    offset = MatcherEntry.size
    pattern_offset_end = offset + pattern_len

    segments = []
    while offset < pattern_offset_end:
        typ, segment_length = Segment.unpack_from(buffer, offset)
        offset += Segment.size
        typ = SegmentType(typ).name.lower()
        data = buffer[offset:offset + segment_length].decode('utf-8')
        offset += segment_length

        segments.append((typ, data))

    methods = buffer[offset:offset + methods_len].strip().decode('ascii') \
        .split()

    return DecodedRoute(route_id, handler_id, segments, methods)


@pytest.mark.parametrize('route',
[
    Route('/', 0, []),
    Route('/', 0, ['GET']),
    Route('/test/{hi}', 0, []),
    Route('/test/{hi}', 0, ['POST'])
], ids=Route.describe)
def test_compile(route):
    decompiled = decompile(compile(route))

    assert decompiled.route_id == id(route)
    assert decompiled.handler_id == id(route.handler)
    assert decompiled.segments == route.segments
    assert decompiled.methods == route.methods
