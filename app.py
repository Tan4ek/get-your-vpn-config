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
from repository.provider_metric import PrometheusOpenvpnProviderMetric, PrometheusShadowsocksProviderMetric
from repository.shadow_socks_api import ShadowSocksApi
from service.invite_service import InviteService
from service.providers_metric_service import ProvidersMetricService

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)

persist = Persistent(config['sqlite']['FilePath'])
openvpn_api = OpenvpnApi(config['openvpn-http-api']['Uri'])
shadow_socks_api = ShadowSocksApi(config['outline-ss-server-user-manager']['Uri'])
invite_service = InviteService(openvpn_api, shadow_socks_api, persist)
admin_controller = AdminController(invite_service, config['admin']['XApiKey'])
invite_controller = InviteController(invite_service, config['get-your-vpn-config']['Host'])
provider_metric = ProvidersMetricService([PrometheusOpenvpnProviderMetric(config['vpn-metrics']['PrometheusUri']),
                                          PrometheusShadowsocksProviderMetric(config['vpn-metrics']['PrometheusUri'])],
                                         persist)


class ScheduleThread(threading.Thread):

    def __init__(self, interval: float = 0.1):
        super().__init__()
        self._event: threading.Event = threading.Event()
        self._interval = interval

    def run(self):
        log.info("Start schedule thread")
        while not self.stopped():
            schedule.run_pending()
            time.sleep(self._interval)

    def stop(self):
        log.info("Schedule thread stop")
        self._event.set()

    def stopped(self):
        return self._event.is_set()


schedule.every(1).hour.do(provider_metric.scrap_metrics)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(admin_controller.blueprint())
    app.register_blueprint(invite_controller.blueprint())

    continuous_thread = ScheduleThread()
    continuous_thread.daemon = True
    continuous_thread.start()
    return app
