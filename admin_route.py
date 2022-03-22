from flask import Blueprint
from flask import jsonify
from flask import request, make_response

from admin_manager import AdminManager


class AdminController:

    def __init__(self, admin_manager: AdminManager):
        self._admin_manager = admin_manager
        self._flask_blueprint = Blueprint('admin-management', __name__, url_prefix="/god")
        self._init_route()

    def _init_route(self):
        app = self._flask_blueprint

        @app.route("/client", methods=['POST'])
        def create_client():
            body = request.get_json()

            description = body.get('description', '')

            invite_code = self._admin_manager.create_invite_code(description)
            return jsonify({
                'code': invite_code.code
            })

        @app.route("/client", methods=['DELETE'])
        def delete_client():
            body = request.get_json()

            code = body['code']
            self._admin_manager.delete_invite_code(code)
            return ''

        @app.route("/clients", methods=['GET'])
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

        @app.route("/invite-code", methods=["GET"])
        def get_invite_code():
            code = request.args.get('code')
            invite_code = self._admin_manager.get_code(code)
            if invite_code:
                return jsonify({
                    "active": True,
                    "openvpn": self._admin_manager.exist_openvpn_provider(invite_code.code)
                })
            else:
                return make_response('', 404)

        @app.route("/provider-openvpn", methods=["POST"])
        def create_provider():
            body = request.get_json()
            invite_code = body.get('invite-code')
            password = body.get('password')
            openvpn_client_provider = self._admin_manager.create_provider_openvpn(invite_code, password)
            return jsonify({
                "ovpn_file": openvpn_client_provider.ovpn_file
            })

    def blueprint(self) -> Blueprint:
        return self._flask_blueprint
