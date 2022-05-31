import base64
import uuid

from flask.testing import FlaskClient
from pytest_httpserver import HTTPServer


def test_admin_get_invites(client: FlaskClient, invite: dict):
    invites_response = client.get('/god/invites', headers={'x-api-key': 'supersecureapikey'})
    assert invites_response.json
    created_invite = [i for i in invites_response.json if i['code'] == invite['code']][0]
    assert invites_response.status_code == 200
    assert created_invite['description']


def test_admin_delete_invite_code(client, invite: dict):
    delete_invite_response = client.delete(f"/god/invite/{invite['code']}", headers={'x-api-key': 'supersecureapikey'})
    assert delete_invite_response.status_code == 200
    assert not delete_invite_response.data

    invites_response = client.get('/god/invites', headers={'x-api-key': 'supersecureapikey'})
    assert not [i for i in invites_response.json if i['code'] == invite['code']]


def test_admin_wrong_api_key_get_invites(client: FlaskClient):
    response = client.get('/god/invites', headers={'x-api-key': 'superwrongkey'})
    assert response.status_code == 401


def test_admin_no_auth_header_get_invites(client: FlaskClient):
    response = client.get('/god/invites')
    assert response.status_code == 401


def test_admin_wrong_api_key_create_invite(client: FlaskClient):
    response = client.post('/god/invite', headers={'x-api-key': 'superwrongkey'}, json={'description': 'olala'})
    assert response.status_code == 401


def test_admin_no_auth_header_create_invite(client: FlaskClient):
    response = client.post('/god/invite', json={'description': 'olala'})
    assert response.status_code == 401


def test_admin_wrong_api_key_delete_invite(client: FlaskClient):
    response = client.delete('/god/invite/SOMETHING', headers={'x-api-key': 'superwrongkey'})
    assert response.status_code == 401


def test_admin_no_auth_header_delete_invite(client: FlaskClient):
    response = client.delete('/god/invite/SOMETHING')
    assert response.status_code == 401


def test_create_ovpn_config(client: FlaskClient, httpserver: HTTPServer, invite: dict):
    httpserver.expect_request("/openvpn/ovpn-config", method='POST').respond_with_data('ovpn_file')

    create_ovpn_response = client.post(f"/invite/{invite['code']}/openvpn",
                                       json={'password': '123456'})
    assert create_ovpn_response.status_code == 200
    assert create_ovpn_response.json['id']
    assert create_ovpn_response.json['ovpn_file'] == base64.b64encode(bytes('ovpn_file', 'utf-8')).decode('utf-8')

    get_ovpn_response = client.get(f"/invite/{invite['code']}/openvpn")
    assert get_ovpn_response.status_code == 200
    assert get_ovpn_response.json[0]['id'] == create_ovpn_response.json['id']
    assert get_ovpn_response.json[0]['ovpn_file'] == create_ovpn_response.json['ovpn_file']

    invite_response = client.get(f"/invite/{invite['code']}")
    assert invite_response.status_code == 200
    assert invite_response.json['active'] is True
    assert invite_response.json['openvpn'][0]['id'] == create_ovpn_response.json['id']
    assert invite_response.json['openvpn'][0]['ovpn_file'] == create_ovpn_response.json['ovpn_file']


def test_create_shadow_socks(client: FlaskClient, httpserver: HTTPServer, invite: dict):
    httpserver.expect_request("/ss-server/user", method='POST').respond_with_json({
        'user_id': 'shadow-socks-test-user-id' + str(uuid.uuid4()),
        'port': '443',
        'cipher': 'chacha20-ietf-poly1305',
        'secret': 'lolipop',
    })

    create_shadow_socks_response = client.post(f"/invite/{invite['code']}/shadow-socks")
    assert create_shadow_socks_response.status_code == 200
    assert create_shadow_socks_response.json['id']
    assert create_shadow_socks_response.json['ssurl'].startswith('ss://')

    get_shadow_socks_response = client.get(f"/invite/{invite['code']}/shadow-socks")
    assert get_shadow_socks_response.status_code == 200
    assert get_shadow_socks_response.json[0]['id'] == create_shadow_socks_response.json['id']
    assert get_shadow_socks_response.json[0]['ssurl'] == create_shadow_socks_response.json['ssurl']

    invite_response = client.get(f"/invite/{invite['code']}")
    assert invite_response.status_code == 200
    assert invite_response.json['active'] is True
    assert invite_response.json['shadow_socks'][0]['id'] == create_shadow_socks_response.json['id']
    assert invite_response.json['shadow_socks'][0]['ssurl'] == create_shadow_socks_response.json['ssurl']
