from collections import namedtuple
import glob
import os.path

import pytoml
import pytest


testcase_fields = 'data,method,path,version,headers,body,error'

HttpTestCase = namedtuple('HTTPTestCase', testcase_fields)


def parametrize_cases(suite, *args):
    suite = suites[suite]
    cases_list = [
        [suite[c] for c in sel.split('+')] for sel in args]
    return pytest.mark.parametrize('cases', cases_list, ids=args)


def load_casefile(path):
    result = {}

    with open(path) as casefile:
        cases = pytoml.load(casefile)

    for case_name, case_data in cases.items():
        print(case_name)
        print(case_data)
        print('*************' * 5)
        """
        11clincomplete_body
        {
        'data': 'POST / HTTP/1.1\r\nContent-Length: 5\r\n\r\nI', 
        'method': 'POST', 
        'path': '/', 
        'version': '1.1', 
        'headers': {'Content-Length': '5'}, 
        'error': 'incomplete_body'
        }
        """
        case_data['data'] = case_data['data'].encode('utf-8')
        case_data['body'] = case_data['body'].encode('utf-8') if 'body' in case_data else None
        case = HttpTestCase._make(
            case_data.get(f) for f in testcase_fields.split(','))
        result[case_name] = case

    return result


def load_cases():
    cases = {}

    for filename in glob.glob('cases/*.toml'):
        suite_name, _ = os.path.splitext(os.path.basename(filename))
        cases[suite_name] = load_casefile(filename)

    return cases


suites = load_cases()
# print(suites)
# print('*************' * 5)
# print(globals())
# print('*************' * 5)
globals().update(suites)
# print(globals())

"""
{'base': {
'10long': HTTPTestCase(data=b'POST /wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg HTTP/1.0\r\nHOST: www.kittyhell.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: ja,en-us;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: Shift_JIS,utf-8;q=0.7,*;q=0.7\r\nKeep-Alive: 115\r\nCookie: wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral\r\n\r\nHello there', method='POST', path='/wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg', version='1.0', headers={'Host': 'www.kittyhell.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'ja,en-us;q=0.7,en;q=0.3', 'Accept-Encoding': 'gzip,deflate', 'Accept-Charset': 'Shift_JIS,utf-8;q=0.7,*;q=0.7', 'Keep-Alive': '115', 'Cookie': 'wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral'}, body=b'Hello there', error=None), 
'10short': HTTPTestCase(data=b'POST / HTTP/1.0\r\nHost: www.example.com\r\n\r\nHi!', method='POST', path='/', version='1.0', headers={'Host': 'www.example.com'}, body=b'Hi!', error=None), 
'10malformed_headers1': HTTPTestCase(data=b'GET / HTTP 1.0', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), 
'10malformed_headers2': HTTPTestCase(data=b'GET / HTTP/2', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), 
'10incomplete_headers': HTTPTestCase(data=b'GET / HTTP/1.0\r\nH', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), 
'11get': HTTPTestCase(data=b'GET /index.html HTTP/1.1\r\n\r\n', method='GET', path='/index.html', version='1.1', headers={}, body=None, error=None), 
'11clget': HTTPTestCase(data=b'GET /body HTTP/1.1\r\nContent-Length: 12\r\n\r\nHello World!', method='GET', path='/body', version='1.1', headers={'Content-Length': '12'}, body=b'Hello World!', error=None), 
'11clkeep': HTTPTestCase(data=b'POST /login HTTP/1.1\r\nContent-Length: 5\r\n\r\nHello', method='POST', path='/login', version='1.1', headers={'Content-Length': '5'}, body=b'Hello', error=None), 
'11clzero': HTTPTestCase(data=b'POST /zero HTTP/1.1\r\nContent-Length: 0\r\n\r\n', method='POST', path='/zero', version='1.1', headers={'Content-Length': '0'}, body=b'', error=None), 
'11clclose': HTTPTestCase(data=b'POST /logout HTTP/1.1\r\nContent-Length: 3\r\nConnection: close\r\n\r\nBye', method='POST', path='/logout', version='1.1', headers={'Content-Length': '3', 'Connection': 'close'}, body=b'Bye', error=None), 
'11clincomplete_headers': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 3\r\nI', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), 
'11clincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 5\r\n\r\nI', method='POST', path='/', version='1.1', headers={'Content-Length': '5'}, body=None, error='incomplete_body'), 
'11chunked1': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\n\r\n4\r\nWiki\r\n5\r\npedia\r\nE\r\n in\r\n\r\nchunks.\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={}, body=b'Wikipedia in\r\n\r\nchunks.', error=None), 
'11chunkedzero': HTTPTestCase(data=b'PUT /zero HTTP/1.1\r\nConnection: close\r\n\r\n0\r\n\r\n', method='PUT', path='/zero', version='1.1', headers={'Connection': 'close'}, body=b'', error=None), 
'11chunked2': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n1;token=123;x=3\r\nr\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={'Transfer-Encoding': 'chunked'}, body=b'r', error=None), 
'11chunked3': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n000002\r\nab\r\n0;q=1\r\nThis: is trailer header\r\n\r\n', method='POST', path='/', version='1.1', headers={}, body=b'ab', error=None), 
'11chunkedincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n10\r\nasd', method='POST', path='/', version='1.1', headers={}, body=None, error='incomplete_body'), 
'11chunkedmalformed_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n1x\r\nhello', method='POST', path='/', version='1.1', headers={}, body=None, error='malformed_body')
}
}

HTTPTestCase(
data=b'POST / HTTP/1.1\r\n\r\n1x\r\nhello', 
method='POST', 
path='/', 
version='1.1', 
headers={}, 
body=None, 
error='malformed_body')




*****************************************************************
{
'__name__': '__main__', 
'__doc__': None, 
'__package__': None, 
'__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f0b0e9c0898>, 
'__spec__': None, 
'__annotations__': {}, 
'__builtins__': <module 'builtins' (built-in)>, 
'__file__': 'cases.py', 
'__cached__': None, 
'namedtuple': <function namedtuple at 0x7f0b0e9001e0>, 
'glob': <module 'glob' from '/usr/lib64/python3.6/glob.py'>, 
'os': <module 'os' from '/usr/lib64/python3.6/os.py'>, 
'pytoml': <module 'pytoml' from '/usr/local/lib/python3.6/site-packages/pytoml/__init__.py'>, 
'pytest': <module 'pytest' from '/usr/local/lib/python3.6/site-packages/pytest.py'>, 
'testcase_fields': 'data,method,path,version,headers,body,error', 
'HttpTestCase': <class '__main__.HTTPTestCase'>, 
'parametrize_cases': <function parametrize_cases at 0x7f0b06eda378>, 
'load_casefile': <function load_casefile at 0x7f0b016940d0>, 
'load_cases': <function load_cases at 0x7f0b01694158>, 
'suites': {'base': {'10long': HTTPTestCase(data=b'POST /wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg HTTP/1.0\r\nHOST: www.kittyhell.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: ja,en-us;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: Shift_JIS,utf-8;q=0.7,*;q=0.7\r\nKeep-Alive: 115\r\nCookie: wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral\r\n\r\nHello there', method='POST', path='/wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg', version='1.0', headers={'Host': 'www.kittyhell.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'ja,en-us;q=0.7,en;q=0.3', 'Accept-Encoding': 'gzip,deflate', 'Accept-Charset': 'Shift_JIS,utf-8;q=0.7,*;q=0.7', 'Keep-Alive': '115', 'Cookie': 'wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral'}, body=b'Hello there', error=None), '10short': HTTPTestCase(data=b'POST / HTTP/1.0\r\nHost: www.example.com\r\n\r\nHi!', method='POST', path='/', version='1.0', headers={'Host': 'www.example.com'}, body=b'Hi!', error=None), '10malformed_headers1': HTTPTestCase(data=b'GET / HTTP 1.0', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), '10malformed_headers2': HTTPTestCase(data=b'GET / HTTP/2', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), '10incomplete_headers': HTTPTestCase(data=b'GET / HTTP/1.0\r\nH', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), '11get': HTTPTestCase(data=b'GET /index.html HTTP/1.1\r\n\r\n', method='GET', path='/index.html', version='1.1', headers={}, body=None, error=None), '11clget': HTTPTestCase(data=b'GET /body HTTP/1.1\r\nContent-Length: 12\r\n\r\nHello World!', method='GET', path='/body', version='1.1', headers={'Content-Length': '12'}, body=b'Hello World!', error=None), '11clkeep': HTTPTestCase(data=b'POST /login HTTP/1.1\r\nContent-Length: 5\r\n\r\nHello', method='POST', path='/login', version='1.1', headers={'Content-Length': '5'}, body=b'Hello', error=None), '11clzero': HTTPTestCase(data=b'POST /zero HTTP/1.1\r\nContent-Length: 0\r\n\r\n', method='POST', path='/zero', version='1.1', headers={'Content-Length': '0'}, body=b'', error=None), '11clclose': HTTPTestCase(data=b'POST /logout HTTP/1.1\r\nContent-Length: 3\r\nConnection: close\r\n\r\nBye', method='POST', path='/logout', version='1.1', headers={'Content-Length': '3', 'Connection': 'close'}, body=b'Bye', error=None), '11clincomplete_headers': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 3\r\nI', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), '11clincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 5\r\n\r\nI', method='POST', path='/', version='1.1', headers={'Content-Length': '5'}, body=None, error='incomplete_body'), '11chunked1': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\n\r\n4\r\nWiki\r\n5\r\npedia\r\nE\r\n in\r\n\r\nchunks.\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={}, body=b'Wikipedia in\r\n\r\nchunks.', error=None), '11chunkedzero': HTTPTestCase(data=b'PUT /zero HTTP/1.1\r\nConnection: close\r\n\r\n0\r\n\r\n', method='PUT', path='/zero', version='1.1', headers={'Connection': 'close'}, body=b'', error=None), '11chunked2': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n1;token=123;x=3\r\nr\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={'Transfer-Encoding': 'chunked'}, body=b'r', error=None), '11chunked3': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n000002\r\nab\r\n0;q=1\r\nThis: is trailer header\r\n\r\n', method='POST', path='/', version='1.1', headers={}, body=b'ab', error=None), '11chunkedincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n10\r\nasd', method='POST', path='/', version='1.1', headers={}, body=None, error='incomplete_body'), '11chunkedmalformed_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n1x\r\nhello', method='POST', path='/', version='1.1', headers={}, body=None, error='malformed_body')}}
}
*****************************************************************
{
'__name__': '__main__', 
'__doc__': None, 
'__package__': None, 
'__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f0b0e9c0898>, 
'__spec__': None, 
'__annotations__': {}, 
'__builtins__': <module 'builtins' (built-in)>, 
'__file__': 'cases.py', 
'__cached__': None, 
'namedtuple': <function namedtuple at 0x7f0b0e9001e0>, 
'glob': <module 'glob' from '/usr/lib64/python3.6/glob.py'>, 
'os': <module 'os' from '/usr/lib64/python3.6/os.py'>, 
'pytoml': <module 'pytoml' from '/usr/local/lib/python3.6/site-packages/pytoml/__init__.py'>, 
'pytest': <module 'pytest' from '/usr/local/lib/python3.6/site-packages/pytest.py'>, 
'testcase_fields': 'data,method,path,version,headers,body,error', 
'HttpTestCase': <class '__main__.HTTPTestCase'>, 
'parametrize_cases': <function parametrize_cases at 0x7f0b06eda378>, 
'load_casefile': <function load_casefile at 0x7f0b016940d0>, 
'load_cases': <function load_cases at 0x7f0b01694158>, 
'suites': {'base': {'10long': HTTPTestCase(data=b'POST /wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg HTTP/1.0\r\nHOST: www.kittyhell.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: ja,en-us;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: Shift_JIS,utf-8;q=0.7,*;q=0.7\r\nKeep-Alive: 115\r\nCookie: wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral\r\n\r\nHello there', method='POST', path='/wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg', version='1.0', headers={'Host': 'www.kittyhell.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'ja,en-us;q=0.7,en;q=0.3', 'Accept-Encoding': 'gzip,deflate', 'Accept-Charset': 'Shift_JIS,utf-8;q=0.7,*;q=0.7', 'Keep-Alive': '115', 'Cookie': 'wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral'}, body=b'Hello there', error=None), '10short': HTTPTestCase(data=b'POST / HTTP/1.0\r\nHost: www.example.com\r\n\r\nHi!', method='POST', path='/', version='1.0', headers={'Host': 'www.example.com'}, body=b'Hi!', error=None), '10malformed_headers1': HTTPTestCase(data=b'GET / HTTP 1.0', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), '10malformed_headers2': HTTPTestCase(data=b'GET / HTTP/2', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), '10incomplete_headers': HTTPTestCase(data=b'GET / HTTP/1.0\r\nH', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), '11get': HTTPTestCase(data=b'GET /index.html HTTP/1.1\r\n\r\n', method='GET', path='/index.html', version='1.1', headers={}, body=None, error=None), '11clget': HTTPTestCase(data=b'GET /body HTTP/1.1\r\nContent-Length: 12\r\n\r\nHello World!', method='GET', path='/body', version='1.1', headers={'Content-Length': '12'}, body=b'Hello World!', error=None), '11clkeep': HTTPTestCase(data=b'POST /login HTTP/1.1\r\nContent-Length: 5\r\n\r\nHello', method='POST', path='/login', version='1.1', headers={'Content-Length': '5'}, body=b'Hello', error=None), '11clzero': HTTPTestCase(data=b'POST /zero HTTP/1.1\r\nContent-Length: 0\r\n\r\n', method='POST', path='/zero', version='1.1', headers={'Content-Length': '0'}, body=b'', error=None), '11clclose': HTTPTestCase(data=b'POST /logout HTTP/1.1\r\nContent-Length: 3\r\nConnection: close\r\n\r\nBye', method='POST', path='/logout', version='1.1', headers={'Content-Length': '3', 'Connection': 'close'}, body=b'Bye', error=None), '11clincomplete_headers': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 3\r\nI', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), '11clincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 5\r\n\r\nI', method='POST', path='/', version='1.1', headers={'Content-Length': '5'}, body=None, error='incomplete_body'), '11chunked1': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\n\r\n4\r\nWiki\r\n5\r\npedia\r\nE\r\n in\r\n\r\nchunks.\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={}, body=b'Wikipedia in\r\n\r\nchunks.', error=None), '11chunkedzero': HTTPTestCase(data=b'PUT /zero HTTP/1.1\r\nConnection: close\r\n\r\n0\r\n\r\n', method='PUT', path='/zero', version='1.1', headers={'Connection': 'close'}, body=b'', error=None), '11chunked2': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n1;token=123;x=3\r\nr\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={'Transfer-Encoding': 'chunked'}, body=b'r', error=None), '11chunked3': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n000002\r\nab\r\n0;q=1\r\nThis: is trailer header\r\n\r\n', method='POST', path='/', version='1.1', headers={}, body=b'ab', error=None), '11chunkedincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n10\r\nasd', method='POST', path='/', version='1.1', headers={}, body=None, error='incomplete_body'), '11chunkedmalformed_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n1x\r\nhello', method='POST', path='/', version='1.1', headers={}, body=None, error='malformed_body')}}, 
'base': {'10long': HTTPTestCase(data=b'POST /wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg HTTP/1.0\r\nHOST: www.kittyhell.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: ja,en-us;q=0.7,en;q=0.3\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: Shift_JIS,utf-8;q=0.7,*;q=0.7\r\nKeep-Alive: 115\r\nCookie: wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral\r\n\r\nHello there', method='POST', path='/wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg', version='1.0', headers={'Host': 'www.kittyhell.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 Pathtraq/0.9', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'ja,en-us;q=0.7,en;q=0.3', 'Accept-Encoding': 'gzip,deflate', 'Accept-Charset': 'Shift_JIS,utf-8;q=0.7,*;q=0.7', 'Keep-Alive': '115', 'Cookie': 'wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; __utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; __utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral'}, body=b'Hello there', error=None), '10short': HTTPTestCase(data=b'POST / HTTP/1.0\r\nHost: www.example.com\r\n\r\nHi!', method='POST', path='/', version='1.0', headers={'Host': 'www.example.com'}, body=b'Hi!', error=None), '10malformed_headers1': HTTPTestCase(data=b'GET / HTTP 1.0', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), '10malformed_headers2': HTTPTestCase(data=b'GET / HTTP/2', method=None, path=None, version=None, headers=None, body=None, error='malformed_headers'), '10incomplete_headers': HTTPTestCase(data=b'GET / HTTP/1.0\r\nH', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), '11get': HTTPTestCase(data=b'GET /index.html HTTP/1.1\r\n\r\n', method='GET', path='/index.html', version='1.1', headers={}, body=None, error=None), '11clget': HTTPTestCase(data=b'GET /body HTTP/1.1\r\nContent-Length: 12\r\n\r\nHello World!', method='GET', path='/body', version='1.1', headers={'Content-Length': '12'}, body=b'Hello World!', error=None), '11clkeep': HTTPTestCase(data=b'POST /login HTTP/1.1\r\nContent-Length: 5\r\n\r\nHello', method='POST', path='/login', version='1.1', headers={'Content-Length': '5'}, body=b'Hello', error=None), '11clzero': HTTPTestCase(data=b'POST /zero HTTP/1.1\r\nContent-Length: 0\r\n\r\n', method='POST', path='/zero', version='1.1', headers={'Content-Length': '0'}, body=b'', error=None), '11clclose': HTTPTestCase(data=b'POST /logout HTTP/1.1\r\nContent-Length: 3\r\nConnection: close\r\n\r\nBye', method='POST', path='/logout', version='1.1', headers={'Content-Length': '3', 'Connection': 'close'}, body=b'Bye', error=None), '11clincomplete_headers': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 3\r\nI', method=None, path=None, version=None, headers=None, body=None, error='incomplete_headers'), '11clincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\nContent-Length: 5\r\n\r\nI', method='POST', path='/', version='1.1', headers={'Content-Length': '5'}, body=None, error='incomplete_body'), '11chunked1': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\n\r\n4\r\nWiki\r\n5\r\npedia\r\nE\r\n in\r\n\r\nchunks.\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={}, body=b'Wikipedia in\r\n\r\nchunks.', error=None), '11chunkedzero': HTTPTestCase(data=b'PUT /zero HTTP/1.1\r\nConnection: close\r\n\r\n0\r\n\r\n', method='PUT', path='/zero', version='1.1', headers={'Connection': 'close'}, body=b'', error=None), '11chunked2': HTTPTestCase(data=b'POST /chunked HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n1;token=123;x=3\r\nr\r\n0\r\n\r\n', method='POST', path='/chunked', version='1.1', headers={'Transfer-Encoding': 'chunked'}, body=b'r', error=None), '11chunked3': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n000002\r\nab\r\n0;q=1\r\nThis: is trailer header\r\n\r\n', method='POST', path='/', version='1.1', headers={}, body=b'ab', error=None), '11chunkedincomplete_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n10\r\nasd', method='POST', path='/', version='1.1', headers={}, body=None, error='incomplete_body'), '11chunkedmalformed_body': HTTPTestCase(data=b'POST / HTTP/1.1\r\n\r\n1x\r\nhello', method='POST', path='/', version='1.1', headers={}, body=None, error='malformed_body')}
}
"""