import impl_cffi


request = "GET /wp-content/uploads/2010/03/hello-kitty-darth-vader-pink.jpg HTTP/1.0\r\n"                                \
    "HOST: www.kittyhell.com\r\n"                                                                                                  \
    "User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; ja-JP-mac; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 "             \
    "Pathtraq/0.9\r\n"                                                                                                             \
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"                                                  \
    "Accept-Language: ja,en-us;q=0.7,en;q=0.3\r\n"                                                                                 \
    "Accept-Encoding: gzip,deflate\r\n"                                                                                            \
    "Accept-Charset: Shift_JIS,utf-8;q=0.7,*;q=0.7\r\n"                                                                            \
    "Keep-Alive: 115\r\n"                                                                                                       \
    "Cookie: wp_ozh_wsa_visits=2; wp_ozh_wsa_visit_lasttime=xxxxxxxxxx; "                                                          \
    "__utma=xxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.xxxxxxxxxx.x; "                                                             \
    "__utmz=xxxxxxxxx.xxxxxxxxxx.x.x.utmccn=(referral)|utmcsr=reader.livedoor.com|utmcct=/reader/|utmcmd=referral\r\n"             \
    "\r\n" \
    "Hello there"
request = request.encode('ascii')

request2 = "GET / HTTP/1.0\r\n" \
    "Host: www.example.com\r\n" \
    "\r\n" \
    "Hi!"
request2 = request2.encode('ascii')


http11_content_length = "POST /login HTTP/1.1\r\n" \
    "Content-Length: 5\r\n" \
    "\r\n" \
    "Hello" \
    "POST /logout HTTP/1.1\r\n" \
    "Content-Length: 3\r\n" \
    "\r\n" \
    "Bye"
http11_content_length = http11_content_length.encode('ascii')

http11_chunked = "POST /chunked HTTP/1.1\r\n" \
    "\r\n" \
    "4\r\n" \
    "Wiki\r\n" \
    "5\r\n" \
    "pedia\r\n" \
    "E\r\n" \
    " in\r\n" \
    "\r\n" \
    "chunks.\r\n" \
    "0\r\n" \
    "\r\n"
http11_chunked = http11_chunked.encode('ascii')

def setup_cffi(dump=True):
    if dump:
        def on_headers(request):
            request.dump_headers()
        def on_error(reason):
            print('- error', reason)
        def on_body(request):
            print('- body -')
            print(request.body)
    else:
        def on_headers(request):
            pass
        def on_error(reason):
            pass
        def on_body(request):
            pass

    return impl_cffi.HttpRequestParser(on_headers, on_error, on_body)


def main():
    cffi_parser = setup_cffi()

    print('---- long')
    cffi_parser.feed(request)
    cffi_parser.feed_disconnect()
    print('---- short')
    cffi_parser.feed(request2)
    cffi_parser.feed_disconnect()
    print('---- error')
    cffi_parser.feed(b'GET / garbage')
    print('---- in parts')
    cffi_parser.feed(request2[:5])
    cffi_parser.feed(request2[5:10])
    cffi_parser.feed(request2[10:])
    cffi_parser.feed_disconnect()
    print('---- body in parts')
    cffi_parser.feed(b"GET / HTTP/1.0\r\n")
    cffi_parser.feed(b"\r\n")
    cffi_parser.feed(b"Hell")
    cffi_parser.feed(b"o World!")
    cffi_parser.feed_disconnect()
    print('---- http 11 content length')
    cffi_parser.feed(http11_content_length)
    cffi_parser.feed_disconnect()
    print('---- http 11 chunked')
    cffi_parser.feed(http11_chunked)
    cffi_parser.feed_disconnect()
    print('---- short')
    cffi_parser.feed(request2)
    cffi_parser.feed_disconnect()
    print('---- http 11 chunked in parts')
    cffi_parser.feed(http11_chunked[:5])
    cffi_parser.feed(http11_chunked[5:10])
    cffi_parser.feed(http11_chunked[10:15])
    cffi_parser.feed(http11_chunked[15:20])
    cffi_parser.feed(http11_chunked[20:30])
    cffi_parser.feed(http11_chunked[30:35])
    cffi_parser.feed(http11_chunked[35:])
    cffi_parser.feed_disconnect()

if __name__ == '__main__':
    main()
