from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# create a tiny in-memory file (PNG header bytes)
file_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00'
files = {'file': ('test.png', file_bytes, 'image/png')}
resp = client.post('/api/upload/', files=files)
print('status', resp.status_code)
print('json', resp.json())
# try to GET the returned URL path
if resp.status_code == 200:
    url = resp.json().get('data', {}).get('url')
    if url:
        # make relative path request
        # TestClient base_url is http://testserver by default; transform to path
        path = url.replace('http://testserver', '')
        print('GET path', path)
        g = client.get(path)
        print('get status', g.status_code)
        print('get headers', g.headers.get('content-type'))
        print('get len', len(g.content))

