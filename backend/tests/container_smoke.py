"""Local-only deployment check. Builds/deploys nothing and uses synthetic data.

Run after `docker build -f backend/Dockerfile -t forces-hq-stage-a-validation:local .`:
    python backend/tests/container_smoke.py
Optional first argument overrides the local image tag. Docker must be available.
"""
import base64
import json
import os
import secrets
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def docker(*args, environment=None):
    result = subprocess.run(['docker', *args], env=environment, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError('Local Docker operation failed; no request or credential is printed')
    return result.stdout.strip()


def main():
    image = sys.argv[1] if len(sys.argv) > 1 else 'forces-hq-stage-a-validation:local'
    token, passphrase = secrets.token_urlsafe(48), secrets.token_urlsafe(24)
    environment = {**os.environ, 'FHQ_API_TOKEN': token}
    container = no_token = None
    try:
        assert docker('image', 'inspect', image, '--format', '{{.Config.User}}') == '10001:10001'
        assert '--no-access-log' in docker('image', 'inspect', image, '--format', '{{json .Config.Cmd}}')
        # Pass the environment variable by NAME, never its secret value in argv.
        container = docker('run', '--detach', '--rm', '--publish', '127.0.0.1::8000', '--env', 'FHQ_API_TOKEN', image, environment=environment)
        port = docker('port', container, '8000/tcp').rsplit(':', 1)[1]
        origin = 'http://127.0.0.1:' + port

        def request(path, method='GET', data=None, authenticated=False):
            headers = {'Authorization': 'Bearer ' + token} if authenticated else {}
            body = None
            if data is not None:
                headers['Content-Type'] = 'application/json'
                body = json.dumps(data).encode()
            try:
                response = urlopen(Request(origin + path, data=body, headers=headers, method=method), timeout=5)
            except HTTPError as response:
                return response.code, response.read(), response.headers
            with response:
                return response.status, response.read(), response.headers

        deadline = time.monotonic() + 30
        while True:
            try:
                status, body, _ = request('/healthz')
                assert status == 200 and json.loads(body) == {'status': 'ok', 'api_version': '1'}
                break
            except (URLError, TimeoutError, OSError):
                if time.monotonic() >= deadline:
                    raise RuntimeError('Local API did not become ready') from None
                time.sleep(.2)

        for path in ('/v1/profile/options', '/v1/capabilities', '/v1/profile', '/v1/profile/backup/export', '/v1/profile/backup/restore'):
            method = 'POST' if '/backup/' in path else 'PUT' if path == '/v1/profile' else 'GET'
            status, body, headers = request(path, method, {} if method != 'GET' else None)
            assert status == 401 and token.encode() not in body
            assert 'no-store' in headers.get('Cache-Control', '')
        for path in ('/docs', '/openapi.json', '/.env', '/policy_data/manifest.json'):
            assert request(path, authenticated=True)[0] == 404
        assert request('/v1/profile/options', authenticated=True)[0] == 200

        document = {'version': 1, 'profile': {'service': 'British Army', 'rank': 'Private / equivalent'}, 'events': []}
        status, body, _ = request('/v1/profile', 'PUT', document, True)
        assert status == 200
        confirmed = json.loads(body)
        assert confirmed['provenance']['policy'] == 'not_assessed'
        assert confirmed['document']['profile']['verified_pensionable_salary'] is None
        status, encrypted, _ = request('/v1/profile/backup/export', 'POST', {'document': confirmed['document'], 'passphrase': passphrase}, True)
        assert status == 200 and encrypted.startswith(b'FHQ1\n') and b'British Army' not in encrypted
        restore = {'encrypted_file': base64.b64encode(encrypted).decode(), 'passphrase': passphrase}
        status, body, _ = request('/v1/profile/backup/restore', 'POST', restore, True)
        assert status == 200 and json.loads(body)['document'] == confirmed['document']
        restore['passphrase'] = 'incorrect-test-passphrase'
        status, body, _ = request('/v1/profile/backup/restore', 'POST', restore, True)
        assert status == 422 and passphrase.encode() not in body
        invalid = {'profile': {'service': 'British Army', 'rank': 'Private / equivalent', 'service_number': 'synthetic-private-marker'}}
        status, body, _ = request('/v1/profile', 'PUT', invalid, True)
        assert status == 422 and b'synthetic-private-marker' not in body
        log_result = subprocess.run(['docker', 'logs', container], capture_output=True, text=True, timeout=15)
        logs = log_result.stdout + log_result.stderr
        assert all(value not in logs for value in (token, passphrase, 'synthetic-private-marker'))
        docker('exec', container, 'python', '-c', 'from pathlib import Path; assert all(not Path(p).exists() for p in ("/app/.env", "/app/.git", "/app/frontend", "/app/policy_data", "/app/app.py", "/run/secrets/build-ca"))')

        # A separate image instance must refuse startup without a token.
        no_token = docker('create', image)
        subprocess.run(['docker', 'start', '--attach', no_token], capture_output=True, timeout=15)
        assert docker('inspect', no_token, '--format', '{{.State.Running}}') == 'false'
        assert docker('inspect', no_token, '--format', '{{.State.ExitCode}}') != '0'
        denied = subprocess.run(['docker', 'logs', no_token], capture_output=True, text=True, timeout=15)
        assert 'Set a strong FHQ_API_TOKEN before starting the API' in denied.stdout + denied.stderr
        print('PASS: non-root container, health, anonymous denial, authenticated profile and encrypted round trip, redacted errors/logs, source whitelist, fail-closed startup')
    finally:
        for identifier in (container, no_token):
            if identifier:
                subprocess.run(['docker', 'rm', '--force', identifier], capture_output=True, timeout=15)


if __name__ == '__main__':
    main()
