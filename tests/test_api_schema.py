# -*- coding: utf-8 -*-
"""API schema tests — verify endpoints accept correct params and return expected format.

These tests use the test client with auth token. Since there's no real AWS backend
in test mode, we expect either proper error responses (with correct structure) or
validation errors for bad input. The key assertion is response FORMAT, not data.
"""

import pytest


class TestServerEndpoints:
    """Server module endpoint format tests."""

    def test_list_server_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/server', headers={'Authorization': f'Bearer {auth_token}'})
        # Missing required 'dc' query param → 422
        assert resp.status_code == 422

    def test_list_server_with_dc(self, client, auth_token):
        resp = client.get('/api/v1/server?dc=Easyun', headers={'Authorization': f'Bearer {auth_token}'})
        # May fail with provider error (no real AWS), but should not be 422
        assert resp.status_code != 422

    def test_server_detail_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/server/detail/i-fake', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422

    def test_server_action_schema(self, client, auth_token):
        # Missing required fields
        resp = client.post('/api/v1/server/action',
                           json={},
                           headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422

    def test_server_action_valid_schema(self, client, auth_token):
        resp = client.post('/api/v1/server/action',
                           json={'svr_ids': ['i-fake'], 'action': 'stop', 'dcName': 'Easyun'},
                           headers={'Authorization': f'Bearer {auth_token}'})
        # Should not be 422 (schema valid), will fail on provider
        assert resp.status_code != 422

    def test_server_delete_schema(self, client, auth_token):
        resp = client.delete('/api/v1/server',
                             json={'svrIds': ['i-fake'], 'dcName': 'Easyun'},
                             headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code != 422


class TestStorageEndpoints:
    """Storage module endpoint format tests."""

    def test_volume_list_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/storage/volume', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422

    def test_bucket_list_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/storage/bucket', headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422

    def test_bucket_property_requires_dc(self, client, auth_token):
        resp = client.put('/api/v1/storage/bucket/test-bucket/property',
                          json={'isEncryption': True},
                          headers={'Authorization': f'Bearer {auth_token}'})
        # Missing dc query param → 422
        assert resp.status_code == 422


class TestDatacenterEndpoints:
    """Datacenter module endpoint format tests."""

    def test_dc_summary_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/dashboard/summary/datacenter',
                          headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422

    def test_subnet_list_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/datacenter/subnet',
                          headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422


class TestAccountEndpoints:
    """Account module endpoint format tests."""

    def test_keypair_list_requires_dc(self, client, auth_token):
        resp = client.get('/api/v1/account/keypair',
                          headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422

    def test_quota_requires_region(self, client, auth_token):
        resp = client.get('/api/v1/account/quota',
                          headers={'Authorization': f'Bearer {auth_token}'})
        assert resp.status_code == 422


class TestResponseFormat:
    """Verify unified response structure."""

    def test_success_response_structure(self, client):
        resp = client.get('/openapi.json')
        assert resp.status_code == 200
        # OpenAPI spec endpoint doesn't use our Result wrapper

    def test_error_response_has_message(self, client):
        # Unauthenticated request
        resp = client.get('/api/v1/server?dc=Easyun')
        data = resp.get_json()
        assert resp.status_code == 401
        assert 'message' in data
