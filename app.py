import configparser
import logging
import threading
import time

import schedule
from flask import Flask

from controller.admin_controller import AdminController
from controller.invite_controller import InviteController
from repository.openvpn_api import OpenvpnApi
from repository.persistant import Persistent
from repository.shadow_socks_api import ShadowSocksApi
from service.invite_service import InviteService

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(level=config.get('logging', 'level', fallback='INFO'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

persist = Persistent(config['sqlite']['FilePath'])
openvpn_api = OpenvpnApi(config['openvpn-http-api']['Uri'])
shadow_socks_api = ShadowSocksApi(config['outline-ss-server-user-manager']['Uri'])
invite_service = InviteService(openvpn_api, shadow_socks_api, persist)
admin_controller = AdminController(invite_service, config['admin']['XApiKey'])
invite_controller = InviteController(invite_service, config['get-your-vpn-config']['Host'])


class ScheduleThread(threading.Thread):

    def __init__(self, interval: float = 0.1):
        super().__init__()
        self._event: threading.Event = threading.Event()
        self._interval = interval

    def run(self):
        while not self.stopped():
            schedule.run_pending()
            time.sleep(self._interval)

    def stop(self):
        print("stop is called")
        self._event.set()

    def stopped(self):
        return self._event.is_set()


def background_job():
    print('Hello from the background thread')


schedule.every(2).seconds.do(background_job)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(admin_controller.blueprint())
    app.register_blueprint(invite_controller.blueprint())

    continuous_thread = ScheduleThread()
    continuous_thread.daemon = True
    continuous_thread.start()
    return app
