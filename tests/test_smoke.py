# -*- coding: utf-8 -*-
"""Smoke tests — verify app starts and basic endpoints respond."""


def test_app_creates(app):
    """App factory works."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_openapi_spec(client):
    """OpenAPI spec is accessible."""
    resp = client.get('/openapi.json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'paths' in data
    assert len(data['paths']) == 81


def test_auth_flow(client):
    """Login returns a token."""
    resp = client.post('/api/v1/user/auth', json={
        'username': 'testuser',
        'password': 'testpass',
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'detail' in data
    assert 'token' in data['detail']


def test_auth_reject_bad_password(client):
    """Bad password is rejected."""
    resp = client.post('/api/v1/user/auth', json={
        'username': 'testuser',
        'password': 'wrongpass',
    })
    assert resp.status_code in (400, 401, 422)


def test_protected_endpoint_requires_token(client):
    """Protected endpoint rejects unauthenticated request."""
    resp = client.get('/api/v1/server?dc=Easyun')
    assert resp.status_code == 401
