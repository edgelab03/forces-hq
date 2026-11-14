"""Stateless profile API. No personal database, policy file routes or calculations."""
import base64
import binascii
import hmac
import os

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

import profile_backup
from app_context import linked_milestones
from backend.models import ExportRequest, ProfileDocument, ProfileResponse, RestoreRequest

MAX_BODY = 256 * 1024


class PrivacyBoundary:
    def __init__(self, app, token):
        self.app, self.token = app, token

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        headers = dict(scope.get('headers', []))
        started = False

        async def private_send(message):
            nonlocal started
            if message['type'] == 'http.response.start':
                started = True
                message['headers'] = list(message.get('headers', [])) + [
                    (b'cache-control', b'no-store, private'),
                    (b'x-content-type-options', b'nosniff'),
                    (b'referrer-policy', b'no-referrer'),
                ]
            await send(message)

        async def reject(status, code):
            await JSONResponse({'error': {'code': code}}, status_code=status)(scope, receive, private_send)

        async def invoke(child_receive):
            try:
                await self.app(scope, child_receive, private_send)
            except Exception:
                # Unexpected serializers/library errors must not log raw profile
                # values or decrypted content through an ASGI traceback.
                if not started:
                    await reject(500, 'internal_error')

        if scope['path'] != '/healthz' and not hmac.compare_digest(headers.get(b'authorization', b''), b'Bearer ' + self.token.encode()):
            return await reject(401, 'unauthorised')
        # Personal information is accepted only in bounded JSON bodies, never URLs.
        if scope.get('query_string'):
            return await reject(400, 'query_parameters_not_supported')
        if scope['method'] in ('POST', 'PUT'):
            if headers.get(b'content-type', b'').split(b';')[0].lower() != b'application/json':
                return await reject(415, 'json_required')
            body = bytearray()
            while True:
                message = await receive()
                if message['type'] == 'http.disconnect':
                    return
                body.extend(message.get('body', b''))
                if len(body) > MAX_BODY:
                    return await reject(413, 'request_too_large')
                if not message.get('more_body', False):
                    break

            async def replay():
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await invoke(replay)
        return await invoke(receive)


def profile_response(document):
    data = document.model_dump(mode='json')
    profile = data['profile']
    return {
        'schema_version': '1', 'document': data,
        'provenance': {'profile': 'user_confirmed', 'salary': 'user_attested' if profile['salary_verified'] else 'not_confirmed', 'policy': 'not_assessed'},
        'storage': 'browser_memory_with_explicit_encrypted_backup',
        'summary': {
            'service': profile['service'], 'rank': profile['rank'],
            'employment_type': profile['employment_type'],
            'milestones': linked_milestones(profile, data['events']),
        },
    }


def create_app(token=None):
    token = token if token is not None else os.environ.get('FHQ_API_TOKEN', '')
    if len(token) < 32 or not token.isascii():
        raise RuntimeError('Set a strong FHQ_API_TOKEN before starting the API')
    app = FastAPI(title='Forces HQ connected foundation', version='1.0.0', docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(PrivacyBoundary, token=token)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exception):
        # FastAPI's default response includes rejected input and can leak passphrases.
        return JSONResponse({'error': {'code': 'invalid_request', 'fields': [
            '.'.join(str(part) for part in error['loc'] if part != 'body') for error in exception.errors()
        ]}}, status_code=422)

    @app.exception_handler(HTTPException)
    async def expected_error(request, exception):
        return JSONResponse({'error': {'code': str(exception.detail)}}, status_code=exception.status_code)

    @app.get('/healthz')
    def health():
        return {'status': 'ok', 'api_version': '1'}

    @app.get('/v1/capabilities')
    def capabilities():
        return {'stage': 'A', 'connected': ['profile', 'encrypted_backup'], 'not_connected': ['money', 'entitlements', 'policy', 'guided_benefits'], 'cloud_sync': False}

    @app.get('/v1/profile/options')
    def options():
        return {'choices': profile_backup.CHOICES, 'pension_schemes': ['AFPS 75', 'AFPS 05', 'AFPS 15', 'RFPS 05', 'Not sure'], 'milestone_labels': profile_backup.EVENT_LABELS}

    @app.post('/v1/profile/validate', response_model=ProfileResponse)
    @app.put('/v1/profile', response_model=ProfileResponse)
    def update_profile(document: ProfileDocument):
        return profile_response(document)

    @app.post('/v1/profile/backup/export')
    def export_profile(request: ExportRequest):
        document = request.document.model_dump(mode='json')
        try:
            encrypted = profile_backup.save(document['profile'], document['events'], request.passphrase.get_secret_value(), benefits=document['benefits'])
        except (ValueError, TypeError, KeyError):
            raise HTTPException(422, 'backup_export_rejected') from None
        return Response(encrypted, media_type='application/octet-stream', headers={'Content-Disposition': 'attachment; filename="forces-hq-profile.fhq"'})

    @app.post('/v1/profile/backup/restore', response_model=ProfileResponse)
    def restore_profile(request: RestoreRequest):
        try:
            encrypted = base64.b64decode(request.encrypted_file, validate=True)
            restored = profile_backup.load(encrypted, request.passphrase.get_secret_value())
            # Old backups may omit service/rank. Require completion rather than inventing them.
            document = ProfileDocument.model_validate(restored)
        except (ValueError, TypeError, KeyError, binascii.Error):
            raise HTTPException(422, 'backup_restore_rejected') from None
        return profile_response(document)

    return app
