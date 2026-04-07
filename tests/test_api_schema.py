# -*- coding: utf-8 -*-
"""API schema tests — verify endpoints accept correct params and return expected format."""

import pytest

DC_HEADER = {'X-Datacenter': 'Easyun'}


def _auth_headers(token, with_dc=True):
    h = {'Authorization': f'Bearer {token}'}
    if with_dc:
        h.update(DC_HEADER)
    return h


class TestServerEndpoints:

    def test_list_server_no_dc_no_422(self, client, auth_token):
        """Without X-Datacenter header, should not be 422 (dc is optional via header now)"""
        resp = client.get('/api/v1/server', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code != 422

    def test_list_server_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/server', headers=_auth_headers(auth_token))
        assert resp.status_code != 422

    def test_server_detail_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/server/detail/i-fake', headers=_auth_headers(auth_token))
        assert resp.status_code != 422

    def test_server_action_schema(self, client, auth_token):
        resp = client.post('/api/v1/server/action', json={}, headers=_auth_headers(auth_token))
        assert resp.status_code == 422

    def test_server_action_valid_schema(self, client, auth_token):
        resp = client.post('/api/v1/server/action',
                           json={'svr_ids': ['i-fake'], 'action': 'stop'},
                           headers=_auth_headers(auth_token))
        assert resp.status_code != 422

    def test_server_delete_schema(self, client, auth_token):
        resp = client.delete('/api/v1/server',
                             json={'svrIds': ['i-fake']},
                             headers=_auth_headers(auth_token))
        assert resp.status_code != 422


class TestStorageEndpoints:

    def test_volume_list_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/storage/volume', headers=_auth_headers(auth_token))
        assert resp.status_code != 422

    def test_bucket_list_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/storage/bucket', headers=_auth_headers(auth_token))
        assert resp.status_code != 422

    def test_bucket_property_with_dc(self, client, auth_token):
        resp = client.put('/api/v1/storage/bucket/test-bucket/property',
                          json={'isEncryption': True},
                          headers=_auth_headers(auth_token))
        assert resp.status_code != 422


class TestDatacenterEndpoints:

    def test_dc_summary_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/dashboard/summary/datacenter', headers=_auth_headers(auth_token))
        # Provider error expected (no DC in test DB), just verify route exists and auth works
        assert resp.status_code not in (401, 404, 405)

    def test_subnet_list_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/datacenter/subnet', headers=_auth_headers(auth_token))
        assert resp.status_code != 422


class TestAccountEndpoints:

    def test_keypair_list_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/account/keypair', headers=_auth_headers(auth_token))
        assert resp.status_code != 422

    def test_quota_requires_region(self, client, auth_token):
        resp = client.get('/api/v1/account/quota', headers=_auth_headers(auth_token))
        assert resp.status_code == 422


class TestResponseFormat:

    def test_success_response_structure(self, client):
        resp = client.get('/openapi.json')
        assert resp.status_code == 200

    def test_error_response_has_message(self, client):
        resp = client.get('/api/v1/server')
        assert resp.status_code == 401
        data = resp.get_json()
        assert 'message' in data
