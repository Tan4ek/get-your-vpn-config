import base64

from flask import Blueprint
from flask import jsonify
from flask import request, make_response

from service.invite_service import InviteService, OpenvpnProviderExistException, ShadowSocksProviderExistException


def encode_base64(text: str):
    return base64.b64encode(bytes(text, 'utf-8')).decode('utf-8')


def generate_ssurl(host: str, port: int, cipher: str, secret: str):
    encoded_uri = base64.b64encode(bytes(f"{cipher}:{secret}@{host}:{port}", 'utf-8')).decode('utf-8')
    return f"ss://{encoded_uri}"


class InviteController:

    def __init__(self, invite_service: InviteService, app_host: str):
        self._invite_service = invite_service
        self._app_host = app_host
        self._flask_blueprint = Blueprint('invite-controller', __name__)
        self._init_route()

    def _init_route(self):
        app = self._flask_blueprint

        @app.get("/invite/<string:code>")
        def get_invite_code(code: str):
            invite_code = self._invite_service.get_code(code)
            if invite_code:
                openvpn_providers = self._invite_service.get_openvpn_providers(code)
                shadow_socks_providers = self._invite_service.get_shadow_socks_providers(code)
                return jsonify({
                    "active": True,
                    "openvpn": [
                        {
                            "id": op.id,
                            "ovpn_file": encode_base64(op.ovpn_file)
                        }
                        for op in openvpn_providers
                    ],
                    "shadow_socks": [
                        {
                            "id": ssp.id,
                            "ssurl": generate_ssurl(self._app_host, ssp.port, ssp.cipher, ssp.secret)
                        }
                        for ssp in shadow_socks_providers
                    ]
                })
            else:
                return make_response('', 404)

        @app.post("/invite/<string:code>/openvpn")
        def create_provider(code):
            body = request.get_json()
            password = body.get('password')
            try:
                openvpn_client_provider = self._invite_service.create_provider_openvpn(code, password)
                if openvpn_client_provider:
                    return jsonify({
                        "id": openvpn_client_provider.id,
                        "ovpn_file": encode_base64(openvpn_client_provider.ovpn_file)
                    })
                else:
                    return make_response('', 404)
            except OpenvpnProviderExistException:
                return make_response(jsonify({
                    "error": "openvpn already exists"
                }), 409)

        @app.post("/invite/<string:code>/shadow-socks")
        def create_shadow_socks_provider(code):
            try:
                shadow_socks_provider = self._invite_service.create_shadow_socks_provider(code)
                if shadow_socks_provider:
                    return jsonify({
                        "id": shadow_socks_provider.id,
                        "ssurl": generate_ssurl(self._app_host, shadow_socks_provider.port,
                                                shadow_socks_provider.cipher, shadow_socks_provider.secret)
                    })
                else:
                    return make_response('', 404)
            except ShadowSocksProviderExistException:
                return make_response(jsonify({
                    "error": "shadow socks already exists"
                }), 409)

        @app.get("/invite/<string:code>/openvpn")
        def get_providers(code):
            openvpn_provider = self._invite_service.get_openvpn_providers(code)
            return jsonify([
                {
                    "id": op.id,
                    "ovpn_file": encode_base64(op.ovpn_file)
                }
                for op in openvpn_provider
            ])

        @app.get("/invite/<string:code>/shadow-socks")
        def get_shadow_socks_providers(code):
            shadow_socks_providers = self._invite_service.get_shadow_socks_providers(code)
            return jsonify([
                {
                    "id": ssp.id,
                    "ssurl": generate_ssurl(self._app_host, ssp.port,
                                            ssp.cipher, ssp.secret)
                }
                for ssp in shadow_socks_providers
            ])

    def blueprint(self) -> Blueprint:
        return self._flask_blueprint
