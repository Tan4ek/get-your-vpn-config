# content of test_sample.py
import os
import tempfile

import requests
from pytest_httpserver import HTTPServer


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5


def test_json_client(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


from app import create_app

import pytest


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()

    yield create_app()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_application(client):
    print(client)
