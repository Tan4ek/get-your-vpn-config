import configparser
import logging

from flask import Flask

from admin_manager import AdminManager
from admin_route import AdminController, InviteCodeController
from openvpn_api import OpenvpnApi
from persistant import Persistent

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(level=config.get('logging', 'level', fallback='INFO'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

persist = Persistent(config['sqlite']['FilePath'])
openvpn_api = OpenvpnApi(config['openvpn-http-api']['Uri'])
admin_manager = AdminManager(openvpn_api, persist)
admin_controller = AdminController(admin_manager, config['admin']['XApiKey'])
invite_controller = InviteCodeController(admin_manager)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(admin_controller.blueprint())
    app.register_blueprint(invite_controller.blueprint())
    return app

