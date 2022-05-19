import requests
from pytest_httpserver import HTTPServer


def test_json_client(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}


def test_admin_invite_code_crud(client):
    create_invite_response = client.post("/god/invite", json={
        'description': 'slow poke'
    }, headers={'x-api-key': 'supersecureapikey'})
    assert create_invite_response.status_code == 200
    assert create_invite_response.json['code']

    invites_response = client.get('/god/invites', headers={'x-api-key': 'supersecureapikey'})
    assert invites_response.json
    created_invite = [i for i in invites_response.json if i['code'] == create_invite_response.json['code']][0]
    assert invites_response.status_code == 200
    assert 'slow poke' == created_invite['description']

    delete_invite_response = client.delete(f"/god/invite/{create_invite_response.json['code']}",
                                           headers={'x-api-key': 'supersecureapikey'})
    assert delete_invite_response.status_code == 200
    assert not delete_invite_response.data

    invites_response = client.get('/god/invites', headers={'x-api-key': 'supersecureapikey'})
    assert not [i for i in invites_response.json if i['code'] == create_invite_response.json['code']]
