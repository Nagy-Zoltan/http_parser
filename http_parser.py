from collections import defaultdict


class InvalidHttpRequest(Exception):
    pass


class HttpParser:

    _METHODS = (
        'GET', 'POST', 'PUT', 'PATCH', 'DELETE',
        'COPY', 'HEAD', 'OPTIONS', 'LINK', 'UNLINK',
        'PURGE', 'LOCK', 'UNLOCK', 'PROPFIND', 'VIEW'
    )
    _URL_START = '/'
    _PROTOCOLS = ('HTTP/0.9', 'HTTP/1.0', 'HTTP/1.1', 'HTTP/2.0')

    _LINE_SEP = '\r\n'
    _HEADER_SEP = ':'

    def __init__(self, http_string):
        self.http_string = http_string
        self._lines = self._get_lines()
        self._request_line = self._get_request_line()
        _parsed_request_line = self._parse_request_line()
        self.method = _parsed_request_line['request_method']
        self.url = _parsed_request_line['url']
        self.protocol = _parsed_request_line['http_protocol']
        _headers_info = self._get_headers_info()
        self.headers = _headers_info['headers']
        self._headers_ending = _headers_info['headers_ending']
        self.payload = self._get_payload()

    def _get_lines(self):
        lines = self.http_string.split(self._LINE_SEP)
        if len(lines) == 1:
            raise InvalidHttpRequest('Could not pares http request.')
        return lines

    def _get_request_line(self):
        return self._lines[0]

    def _parse_request_line(self):
        if self._request_line.count(' ') != 2:
            raise InvalidHttpRequest(f'Invalid requst line: {self._request_line}')
        parts = self._request_line.split()
        if len(parts) != 3:
            raise InvalidHttpRequest(f'Invalid requst line: {self._request_line}')

        request_method, url, http_protocol = parts

        if request_method not in self._METHODS:
            raise InvalidHttpRequest(f'Invalid request method: {request_method}')

        if not url.startswith(self._URL_START):
            raise InvalidHttpRequest(f'Invalid url: {url}')

        if http_protocol not in self._PROTOCOLS:
            raise InvalidHttpRequest(f'Unsupported http protocol: {http_protocol}')

        return {
            'request_method': request_method,
            'url': url,
            'http_protocol': http_protocol
        }

    def _get_headers_info(self):
        headers = defaultdict(list)
        for i, line in enumerate(self._lines[1:], 1):
            if line:
                split_line = line.split(self._HEADER_SEP, maxsplit=1)
                if len(split_line) != 2:
                    raise InvalidHttpRequest(f'Invalid header line: {line}')
                header_name, header_value = split_line
                headers[header_name].append(header_value.strip())
            else:
                headers_ending = i
                break
        else:
            raise InvalidHttpRequest('<CRLF> missing after headers.')

        return {
            'headers': headers,
            'headers_ending': headers_ending
        }

    def _get_payload(self):
        return self.http_string.split(self._LINE_SEP, maxsplit=self._headers_ending)[-1][2:]
