import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def append_config():
    os.environ["GET_YOUR_VPN_CONFIG_PATH"] = 'tests/test_config.ini'


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return "localhost", 9010


@pytest.fixture()
def app(append_config):
    db_fd, db_path = tempfile.mkstemp()

    from app import create_app

    yield create_app()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def invite(client):
    response = client.post("/god/invite", json={
        'description': 'fixture invite code'
    }, headers={'x-api-key': 'supersecureapikey'})
    assert response.status_code == 200
    return response.json
