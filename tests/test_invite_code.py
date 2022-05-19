import base64
import uuid

from flask.testing import FlaskClient
from pytest_httpserver import HTTPServer


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


def test_create_ovpn_config(client: FlaskClient, httpserver: HTTPServer):
    httpserver.expect_request("/openvpn/ovpn-config", method='POST').respond_with_data('ovpn_file')

    create_invite_response = client.post("/god/invite", json={
        'description': 'slow poke'
    }, headers={'x-api-key': 'supersecureapikey'})

    create_ovpn_response = client.post(f"/invite/{create_invite_response.json['code']}/openvpn",
                                       json={'password': '123456'})
    assert create_ovpn_response.status_code == 200
    assert create_ovpn_response.json['id']
    assert create_ovpn_response.json['ovpn_file'] == base64.b64encode(bytes('ovpn_file', 'utf-8')).decode('utf-8')

    get_ovpn_response = client.get(f"/invite/{create_invite_response.json['code']}/openvpn")
    assert get_ovpn_response.status_code == 200
    assert get_ovpn_response.json[0]['id'] == create_ovpn_response.json['id']
    assert get_ovpn_response.json[0]['ovpn_file'] == create_ovpn_response.json['ovpn_file']

    invite_response = client.get(f"/invite/{create_invite_response.json['code']}")
    assert invite_response.status_code == 200
    assert invite_response.json['active'] is True
    assert invite_response.json['openvpn'][0]['id'] == create_ovpn_response.json['id']
    assert invite_response.json['openvpn'][0]['ovpn_file'] == create_ovpn_response.json['ovpn_file']


def test_create_shadow_socks(client: FlaskClient, httpserver: HTTPServer):
    httpserver.expect_request("/ss-server/user", method='POST').respond_with_json({
        'user_id': 'shadow-socks-test-user-id' + str(uuid.uuid4()),
        'port': '443',
        'cipher': 'chacha20-ietf-poly1305',
        'secret': 'lolipop',
    })

    create_invite_response = client.post("/god/invite", json={
        'description': 'slow poke'
    }, headers={'x-api-key': 'supersecureapikey'})

    create_shadow_socks_response = client.post(f"/invite/{create_invite_response.json['code']}/shadow-socks")
    assert create_shadow_socks_response.status_code == 200
    assert create_shadow_socks_response.json['id']
    assert create_shadow_socks_response.json['ssurl'].startswith('ss://')

    get_shadow_socks_response = client.get(f"/invite/{create_invite_response.json['code']}/shadow-socks")
    assert get_shadow_socks_response.status_code == 200
    assert get_shadow_socks_response.json[0]['id'] == create_shadow_socks_response.json['id']
    assert get_shadow_socks_response.json[0]['ssurl'] == create_shadow_socks_response.json['ssurl']

    invite_response = client.get(f"/invite/{create_invite_response.json['code']}")
    assert invite_response.status_code == 200
    assert invite_response.json['active'] is True
    assert invite_response.json['shadow_socks'][0]['id'] == create_shadow_socks_response.json['id']
    assert invite_response.json['shadow_socks'][0]['ssurl'] == create_shadow_socks_response.json['ssurl']
