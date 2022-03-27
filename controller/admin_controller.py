from functools import wraps

from flask import request, make_response, jsonify, Blueprint

from service.invite_service import InviteService


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

    def __init__(self, invite_service: InviteService, x_api_key: str):
        self._invite_service = invite_service
        self._flask_blueprint = Blueprint('admin-controller', __name__, url_prefix="/god")
        self._init_route()
        self.__x_api_key = x_api_key

    def _init_route(self):
        app = self._flask_blueprint

        @app.post("/invite")
        @self.token_required
        def create_client():
            body = request.get_json()

            description = body.get('description', '')

            invite_code = self._invite_service.create_invite_code(description)
            return jsonify({
                'code': invite_code.code
            })

        @app.delete("/invite/<string:code>")
        @self.token_required
        def delete_client(code):
            self._invite_service.delete_invite_code(code)
            return ''

        @app.get("/invites")
        @self.token_required
        def clients():
            return jsonify(self._invite_service.get_codes())

    def blueprint(self) -> Blueprint:
        return self._flask_blueprint
