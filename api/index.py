import sys
import os
import io
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Setup Python module search paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
back_dir = os.path.join(parent_dir, "Back")
vendor_dir = os.path.join(back_dir, "vendor")

for p in [vendor_dir, back_dir, current_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.main import app as fastapi_app
except Exception as e:
    import traceback
    tb = traceback.format_exc()
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "Backend load error", "traceback": {repr(tb)}}}'.encode('utf-8'))
        def do_POST(self):
            self.do_GET()
        def do_PUT(self):
            self.do_GET()
        def do_DELETE(self):
            self.do_GET()
        def do_OPTIONS(self):
            self.do_GET()
else:
    import asyncio

    class handler(BaseHTTPRequestHandler):
        def _handle_request(self, method: str):
            parsed_url = urllib.parse.urlparse(self.path)
            path = parsed_url.path
            query_string = parsed_url.query.encode('latin-1')

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''

            # Prepare ASGI scope
            headers_list = []
            for k, v in self.headers.items():
                headers_list.append((k.lower().encode('latin-1'), v.encode('latin-1')))

            response_status = [200]
            response_headers = []
            response_chunks = []

            scope = {
                'type': 'http',
                'http_version': '1.1',
                'method': method,
                'path': path,
                'raw_path': path.encode('latin-1'),
                'query_string': query_string,
                'headers': headers_list,
                'server': ('127.0.0.1', 80),
                'client': ('127.0.0.1', 0),
            }

            async def receive():
                return {
                    'type': 'http.request',
                    'body': body,
                    'more_body': False
                }

            async def send(message):
                if message['type'] == 'http.response.start':
                    response_status[0] = message['status']
                    for h_k, h_v in message.get('headers', []):
                        response_headers.append((h_k.decode('latin-1'), h_v.decode('latin-1')))
                elif message['type'] == 'http.response.body':
                    response_chunks.append(message.get('body', b''))

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(fastapi_app(scope, receive, send))
                loop.close()
            except Exception as req_err:
                import traceback
                response_status[0] = 500
                response_headers = [('content-type', 'application/json')]
                response_chunks = [f'{{"error": "Request Error", "detail": {repr(traceback.format_exc())}}}'.encode('utf-8')]

            # Send HTTP response
            self.send_response(response_status[0])
            for h_k, h_v in response_headers:
                if h_k.lower() not in ('transfer-encoding',):
                    self.send_header(h_k, h_v)
            self.end_headers()
            self.wfile.write(b''.join(response_chunks))

        def do_GET(self):
            self._handle_request('GET')

        def do_POST(self):
            self._handle_request('POST')

        def do_PUT(self):
            self._handle_request('PUT')

        def do_DELETE(self):
            self._handle_request('DELETE')

        def do_OPTIONS(self):
            self._handle_request('OPTIONS')

        def do_PATCH(self):
            self._handle_request('PATCH')
