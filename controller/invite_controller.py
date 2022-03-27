import base64

from flask import Blueprint
from flask import jsonify
from flask import request, make_response

from service.invite_service import InviteService, OpenvpnProviderExistException


class InviteController:

    def __init__(self, invite_service: InviteService):
        self._invite_service = invite_service
        self._flask_blueprint = Blueprint('invite-controller', __name__)
        self._init_route()

    def _init_route(self):
        app = self._flask_blueprint

        @app.get("/invite/<string:code>")
        def get_invite_code(code: str):
            invite_code = self._invite_service.get_code(code)
            if invite_code:
                openvpn_provider = self._invite_service.get_openvpn_providers(code)
                return jsonify({
                    "active": True,
                    "openvpn": [
                        {
                            "id": op.id,
                            "ovpn_file": base64.b64encode(bytes(op.ovpn_file, 'utf-8')).decode('utf-8')
                        }
                        for op in openvpn_provider
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
                        "ovpn_file": base64.b64encode(bytes(openvpn_client_provider.ovpn_file, 'utf-8')).decode('utf-8')
                    })
                else:
                    return make_response('', 404)
            except OpenvpnProviderExistException:
                return make_response(jsonify({
                    "error": "openvpn already exists"
                }), 409)

        @app.get("/invite/<string:code>/openvpn")
        def get_providers(code):
            openvpn_provider = self._invite_service.get_openvpn_providers(code)
            return jsonify([
                {
                    "id": op.id,
                    "ovpn_file": base64.b64encode(bytes(op.ovpn_file, 'utf-8')).decode('utf-8')
                }
                for op in openvpn_provider
            ])

    def blueprint(self) -> Blueprint:
        return self._flask_blueprint
