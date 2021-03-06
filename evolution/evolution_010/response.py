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
