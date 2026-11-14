"""Check built Next.js access gates locally; never connects to an external API.

Requires an existing `npm run build` in frontend/ and Node.js on PATH.
Uses temporary loopback servers and in-memory synthetic credentials only.
"""
import base64
from contextlib import contextmanager
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request(origin, path, auth=None, method='GET', body=None, extra_headers=None):
    headers = dict(extra_headers or {})
    if auth:
        headers['Authorization'] = auth
    data = None if body is None else json.dumps(body).encode()
    if body is not None:
        headers['Content-Type'] = 'application/json'
    try:
        response = urlopen(Request(origin + path, data=data, headers=headers, method=method), timeout=5)
    except HTTPError as response:
        return response.code, response.read(), response.headers
    with response:
        return response.status, response.read(), response.headers


@contextmanager
def preview(username='', password=''):
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    origin = 'http://127.0.0.1:' + str(port)
    environment = {**os.environ, 'FHQ_ACCESS_USERNAME': username, 'FHQ_ACCESS_PASSWORD': password,
                   'FHQ_API_URL': '', 'FHQ_API_TOKEN': '', 'FHQ_ALLOW_LOCAL_API': '', 'FHQ_FRONTEND_ORIGIN': origin}
    folder = Path(__file__).resolve().parents[2] / 'frontend'
    with tempfile.TemporaryFile() as logs:
        process = subprocess.Popen(['node', 'node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', str(port)], cwd=folder, env=environment, stdout=logs, stderr=logs, start_new_session=True)
        try:
            deadline = time.monotonic() + 30
            while True:
                try:
                    request(origin, '/')
                    break
                except (URLError, OSError, TimeoutError):
                    if process.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError('Local Next.js guard check could not start') from None
                    time.sleep(.2)
            yield origin
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=10)


def main():
    with preview() as origin:
        for path in ('/', '/me', '/api/backend/profile/options'):
            status, body, _ = request(origin, path)
            assert status == 503 and json.loads(body)['error']['code'] == 'access_not_configured'
    username, password = 'synthetic-staging-user', secrets.token_urlsafe(32)
    auth = 'Basic ' + base64.b64encode((username + ':' + password).encode()).decode()
    with preview(username, password) as origin:
        for path in ('/', '/me', '/api/backend/profile/options'):
            status, body, headers = request(origin, path)
            assert status == 401 and password.encode() not in body
            assert 'no-store' in headers.get('Cache-Control', '')
        wrong = 'Basic ' + base64.b64encode(b'wrong:wrong').decode()
        assert request(origin, '/me', wrong)[0] == 401
        assert request(origin, '/me', auth)[0] == 200
        status, body, _ = request(origin, '/api/backend/profile/options', auth)
        assert status == 503 and json.loads(body)['error']['code'] == 'backend_not_configured'
        assert request(origin, '/api/backend/policy_data/manifest.json', auth)[0] == 404
        assert request(origin, '/api/backend/profile', auth, 'PUT', {}, {'Origin': 'https://untrusted.invalid'})[0] == 403
    print('PASS: Next.js fails closed without configuration; anonymous/wrong-password requests denied; backend omission, origin and path boundaries enforced')


if __name__ == '__main__':
    main()
