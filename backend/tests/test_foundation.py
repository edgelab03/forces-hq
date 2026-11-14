import base64
from copy import deepcopy
from datetime import date
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import profile_backup
from backend.api import create_app
from benefit_journeys import empty_progress

TOKEN = 'test-only-api-credential-with-32-plus-characters'
PASSWORD = 'test-only-backup-passphrase'


def document():
    return {'version': 1, 'profile': {'service': 'British Army', 'rank': 'Private / equivalent', 'join_date': '2020-01-01', 'dob': '2000-01-01', 'years': 4}, 'events': [], 'benefits': None}


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TOKEN)
        self.client = TestClient(self.app, headers={'Authorization': 'Bearer ' + TOKEN})
        self.addCleanup(self.client.close)

    def test_startup_is_fail_closed(self):
        for token in ('', 'short', '秘密' * 32):
            with self.assertRaises(RuntimeError): create_app(token)

    def test_auth_health_and_no_internal_or_policy_routes(self):
        with TestClient(self.app) as anonymous:
            self.assertEqual(anonymous.get('/v1/profile/options').status_code, 401)
            self.assertEqual(anonymous.get('/healthz').json(), {'status': 'ok', 'api_version': '1'})
        for path in ('/docs', '/openapi.json', '/policy_data/manifest.json', '/v1/policies/../../.env'):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_options_use_existing_vocabulary_and_capabilities_are_honest(self):
        self.assertEqual(self.client.get('/v1/profile/options').json()['choices'], profile_backup.CHOICES)
        capabilities = self.client.get('/v1/capabilities').json()
        self.assertEqual(capabilities['connected'], ['profile', 'encrypted_backup'])
        self.assertFalse(capabilities['cloud_sync'])

    def test_profile_validation_returns_confirmed_context_not_eligibility_or_pay(self):
        response = self.client.put('/v1/profile', json=document())
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result['summary']['rank'], 'Private / equivalent')
        self.assertEqual(result['provenance']['policy'], 'not_assessed')
        self.assertIsNone(result['document']['profile']['verified_pensionable_salary'])
        self.assertEqual(result['storage'], 'browser_memory_with_explicit_encrypted_backup')
        self.assertEqual(response.headers['cache-control'], 'no-store, private')
        self.assertNotIn('eligibility', result)
        self.assertEqual(self.client.post('/v1/profile/validate', json=document()).json(), result)

    def test_both_schemes_and_user_attested_salary_preserve_meaning(self):
        value = document(); value['profile'].update(pension_schemes=['AFPS 05', 'AFPS 15'], verified_pensionable_salary=47000, salary_verified=True)
        result = self.client.put('/v1/profile', json=value)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()['provenance']['salary'], 'user_attested')
        self.assertEqual(result.json()['document']['profile']['pension_schemes'], ['AFPS 05', 'AFPS 15'])

    def test_invalid_values_unknown_pii_and_contradictory_dates_are_rejected(self):
        for changes in (
            {'service_number': 'PRIVATE-SENTINEL'}, {'rank': 'Invented'}, {'dependent_count': -1},
            {'years': True}, {'salary_verified': 'yes'}, {'dob': '2090-01-01'}, {'dob': 1234},
            {'dob': '2021-01-01'}, {'planned_exit': '2019-01-01'},
            {'pension_schemes': ['Not sure', 'AFPS 15']},
            {'rank_history': [{'rank': 'Sergeant', 'date': '2010-01-01'}]},
            {'join_date': None, 'join_date_set': True}, {'salary_verified': True},
        ):
            with self.subTest(changes=changes):
                value = document(); value['profile'].update(changes)
                response = self.client.put('/v1/profile', json=value)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertNotIn('PRIVATE-SENTINEL', response.text)
                self.assertNotIn('input', response.json()['error'])

    def test_provenance_cannot_be_upgraded_by_client(self):
        value = document(); value['profile']['provenance'] = 'document_checked'
        self.assertEqual(self.client.put('/v1/profile', json=value).status_code, 422)

    def test_promotion_and_confirmed_career_dates_are_shared_in_home_summary(self):
        value = document(); value['profile']['rank_history'] = [{'rank': 'Corporal / equivalent', 'date': '2024-02-01'}]
        value['events'] = [{'label': 'Course / qualification', 'date': '2030-01-01'}]
        response = self.client.put('/v1/profile', json=value)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['summary']['milestones'], [{'label': 'Promotion: Corporal / equivalent', 'date': '2024-02-01'}, {'label': 'Course / qualification', 'date': '2030-01-01'}])

    def test_export_is_existing_streamlit_format_and_restore_preserves_progress(self):
        value = document(); value['benefits'] = {'fhtb': empty_progress()}
        value['benefits']['fhtb'].update(interested=True, step='Budget', budget={'price': 200000.0, 'deposit': 20000.0})
        value['events'] = [{'label': 'MPAR', 'date': '2030-01-01'}]
        exported = self.client.post('/v1/profile/backup/export', json={'document': value, 'passphrase': PASSWORD})
        self.assertEqual(exported.status_code, 200, exported.text)
        self.assertTrue(exported.content.startswith(profile_backup.MAGIC))
        self.assertNotIn(b'British Army', exported.content)
        shared = profile_backup.load(exported.content, PASSWORD)
        self.assertEqual(shared['benefits']['fhtb']['budget']['price'], 200000)
        restored = self.client.post('/v1/profile/backup/restore', json={'encrypted_file': base64.b64encode(exported.content).decode(), 'passphrase': PASSWORD})
        self.assertEqual(restored.status_code, 200, restored.text)
        self.assertEqual(restored.json()['document']['benefits'], shared['benefits'])
        self.assertEqual(restored.json()['document']['events'][0]['date'], '2030-01-01')

    def test_old_streamlit_file_is_compatible_and_unsafe_free_text_stays_excluded(self):
        profile = {'service': 'Royal Navy', 'rank': 'Warrant Officer Class 1', 'posting_location': 'PRIVATE-SENTINEL', 'rank_history': [{'rank': 'Sergeant', 'date': '2022-01-01', 'note': 'PRIVATE-SENTINEL'}]}
        data = profile_backup.save(profile, [], PASSWORD)
        response = self.client.post('/v1/profile/backup/restore', json={'encrypted_file': base64.b64encode(data).decode(), 'passphrase': PASSWORD})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn('PRIVATE-SENTINEL', response.text)
        self.assertEqual(response.json()['document']['profile']['rank'], profile['rank'])

    def test_invalid_backup_and_passphrase_errors_never_echo_secrets(self):
        data = profile_backup.save(document()['profile'], [], PASSWORD)
        for encrypted, password in ((data, 'WRONG-PRIVATE-SENTINEL'), (b'invalid', PASSWORD), (data[:-8] + b'tampered', PASSWORD)):
            response = self.client.post('/v1/profile/backup/restore', json={'encrypted_file': base64.b64encode(encrypted).decode(), 'passphrase': password})
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(password, response.text)
            self.assertNotIn(base64.b64encode(encrypted).decode(), response.text)
        response = self.client.post('/v1/profile/backup/export', json={'document': document(), 'passphrase': 'SECRET'})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn('SECRET', response.text)

    def test_incomplete_legacy_file_does_not_create_fictional_service(self):
        data = profile_backup.save({'rank': 'Sergeant'}, [], PASSWORD)
        response = self.client.post('/v1/profile/backup/restore', json={'encrypted_file': base64.b64encode(data).decode(), 'passphrase': PASSWORD})
        self.assertEqual(response.status_code, 422)

    def test_size_content_type_json_and_query_boundaries(self):
        self.assertEqual(self.client.put('/v1/profile', content=b'x' * (256 * 1024 + 1), headers={'Content-Type': 'application/json'}).status_code, 413)
        self.assertEqual(self.client.put('/v1/profile', content='private data').status_code, 415)
        malformed = self.client.put('/v1/profile', content='{PRIVATE-SENTINEL', headers={'Content-Type': 'application/json'})
        self.assertEqual(malformed.status_code, 422)
        self.assertNotIn('PRIVATE-SENTINEL', malformed.text)
        self.assertEqual(self.client.get('/v1/profile/options?profile=secret').status_code, 400)

    def test_instances_and_clients_do_not_share_a_profile_store(self):
        self.client.put('/v1/profile', json=document())
        self.assertEqual(self.client.get('/v1/profile').status_code, 405)
        with TestClient(create_app(TOKEN), headers={'Authorization': 'Bearer ' + TOKEN}) as other:
            self.assertEqual(other.get('/v1/profile').status_code, 405)

    def test_openapi_contract_has_no_public_file_or_diagnostic_endpoint(self):
        paths = self.app.openapi()['paths']
        self.assertEqual(set(paths), {'/healthz', '/v1/capabilities', '/v1/profile/options', '/v1/profile/validate', '/v1/profile', '/v1/profile/backup/export', '/v1/profile/backup/restore'})

    def test_unexpected_library_error_is_sanitised_without_rethrowing_payload(self):
        with patch('backend.api.profile_backup.save', side_effect=RuntimeError('PRIVATE-SENTINEL')):
            response = self.client.post('/v1/profile/backup/export', json={'document': document(), 'passphrase': PASSWORD})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'error': {'code': 'internal_error'}})
        self.assertNotIn('PRIVATE-SENTINEL', response.text)


if __name__ == '__main__': unittest.main()
