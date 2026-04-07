# -*- coding: utf-8 -*-
"""Shared test fixtures."""

import pytest
from easyun import create_app, db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('test')
    with app.app_context():
        _db.create_all()
        # 插入最小必要数据
        from easyun.common.models import Account, User
        if not Account.query.first():
            acct = Account()
            acct.cloud = 'aws'
            acct.account_id = '000000000000'
            acct.deploy_region = 'us-east-1'
            acct.aws_type = 'China'
            _db.session.add(acct)
        if not User.query.first():
            user = User(username='testuser')
            user.set_password('testpass123')
            _db.session.add(user)
        _db.session.commit()
        yield app
        _db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def auth_token(client):
    """Get auth token for protected endpoints."""
    resp = client.post('/api/v1/user/auth', json={
        'username': 'testuser',
        'password': 'testpass123',
    })
    data = resp.get_json()
    return data.get('detail', {}).get('token', '')
