import base64
from functools import wraps

from flask import Blueprint
from flask import jsonify
from flask import request, make_response

from admin_manager import AdminManager, OpenvpnProviderExist


class AdminController:

    def token_required(self, f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            if 'x-api-key' in request.headers:
                token = request.headers['x-api-key']
            if not token or token != self.__x_api_key:
                return make_response(jsonify({"message": "token invalid"}), 401)
            return f(*args, **kwargs)

        return decorator

    def __init__(self, admin_manager: AdminManager, x_api_key: str):
        self._admin_manager = admin_manager
        self._flask_blueprint = Blueprint('admin-management', __name__, url_prefix="/god")
        self._init_route()
        self.__x_api_key = x_api_key

    def _init_route(self):
        app = self._flask_blueprint

        @app.post("/invite")
        @self.token_required
        def create_client():
            body = request.get_json()

            description = body.get('description', '')

            invite_code = self._admin_manager.create_invite_code(description)
            return jsonify({
                'code': invite_code.code
            })

        @app.delete("/invite/<string:code>")
        @self.token_required
        def delete_client(code):
            self._admin_manager.delete_invite_code(code)
            return ''

        @app.get("/invites")
        @self.token_required
        def clients():
            return jsonify(self._admin_manager.get_codes())

    def blueprint(self) -> Blueprint:
        return self._flask_blueprint


class InviteCodeController:

    def __init__(self, admin_manager: AdminManager):
        self._admin_manager = admin_manager
        self._flask_blueprint = Blueprint('invite-code', __name__)
        self._init_route()

    def _init_route(self):
        app = self._flask_blueprint

        @app.get("/invite/<string:code>")
        def get_invite_code(code: str):
            invite_code = self._admin_manager.get_code(code)
            if invite_code:
                openvpn_provider = self._admin_manager.get_openvpn_providers(code)
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
                openvpn_client_provider = self._admin_manager.create_provider_openvpn(code, password)
                if openvpn_client_provider:
                    return jsonify({
                        "id": openvpn_client_provider.id,
                        "ovpn_file": base64.b64encode(bytes(openvpn_client_provider.ovpn_file, 'utf-8')).decode('utf-8')
                    })
                else:
                    return make_response('', 404)
            except OpenvpnProviderExist:
                return make_response(jsonify({
                    "error": "openvpn already exists"
                }), 409)

        @app.get("/invite/<string:code>/openvpn")
        def get_providers(code):
            openvpn_provider = self._admin_manager.get_openvpn_providers(code)
            return jsonify([
                {
                    "id": op.id,
                    "ovpn_file": base64.b64encode(bytes(op.ovpn_file, 'utf-8')).decode('utf-8')
                }
                for op in openvpn_provider
            ])

    def blueprint(self) -> Blueprint:
        return self._flask_blueprint
