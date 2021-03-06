import asyncio
import uvloop
import impl_cext
import signal


response = [
    b'HTTP/1.1 200 OK\r\n',
    b'Connection: keep-alive\r\n',
    b'Content-Length: '
]


class HttpProtocol(asyncio.Protocol):
    def __init__(self, loop):
        print('__init__')
        self.parser = impl_cext.HttpRequestParser(
            self.on_headers, self.on_body, self.on_error)
        self.loop = loop

    def connection_made(self, transport):
        print('connection_made')
        self.transport = transport

    def connection_lost(self, exc):
        print('connection_lost')
        self.parser.feed_disconnect()

    def data_received(self, data):
        print('data_received')
        self.parser.feed(data)

    def on_headers(self, request):
        print('on_headers')
        print(request)  # <HttpRequest GET / 1.1, 3 headers>
        request.dump_headers()
        return

    def on_body(self, request):
        print('on_body')
        print(request)  # <HttpRequest GET / 1.1, 3 headers>
        print(request.body)
        self.loop.create_task(handle_request(request, self.transport))

    def on_error(self, error):
        print('on_error')
        print(error)


class Response:
    __slots__ = ('status_code', 'mime_type', 'text', 'encoding')

    def __init__(self, status_code=200, text='', mime_type='text/plain', encoding='utf-8'):
        self.status_code = 200
        self.mime_type = mime_type
        self.text = text
        self.encoding = encoding

    def render(self):
        data = ['HTTP/1.1 ', str(self.status_code),  ' OK\r\n']
        data.append('Connection: keep-alive\r\n')
        body = self.text.encode(self.encoding)
        data.extend(['Content-Type: ', self.mime_type, '; encoding=', self.encoding, '\r\n'])
        data.extend(['Content-Length: ', str(len(body)), '\r\n\r\n'])

        return ''.join(data).encode(self.encoding) + body


async def handle_request(request, transport):
    if(request.path == '/'):
        response = Response(text='Hello world!')
    elif(request.path == '/dump'):
        response = Response()
        data = [
            'method: ', request.method, '\r\n',
            'path: ', request.path, '\r\n',
            'version: ', request.version, '\r\n',
            'headers:\r\n'
        ]

        for h, v in request.headers.items():
            data.extend([h, ': ', v, '\r\n'])
        response.text = ''.join(data)

    transport.write(response.render())


def serve():
    loop = uvloop.new_event_loop()

    server_coro = loop.create_server(
        lambda: HttpProtocol(loop), '0.0.0.0', 8080, reuse_port=True)

    server = loop.run_until_complete(server_coro)

    loop.add_signal_handler(signal.SIGTERM, loop.stop)
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    serve()
