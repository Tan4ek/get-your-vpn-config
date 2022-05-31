import configparser
import logging
import os

from flask import Flask
from flask_apscheduler import APScheduler

from controller.admin_controller import AdminController
from controller.invite_controller import InviteController
from repository.openvpn_api import OpenvpnApi
from repository.persistent import Persistent
from repository.provider_metric import PrometheusOpenvpnProviderMetric, PrometheusShadowsocksProviderMetric
from repository.shadow_socks_api import ShadowSocksApi
from service.invite_service import InviteService
from service.providers_metric_service import ProvidersMetricService

config = configparser.ConfigParser()
config.read(os.getenv('GET_YOUR_VPN_CONFIG_PATH', default='config.ini'))

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


def create_app():
    app = Flask(__name__)
    app.register_blueprint(admin_controller.blueprint())
    app.register_blueprint(invite_controller.blueprint())

    scheduler = APScheduler()

    @scheduler.task('interval', id='scrap_metrics', seconds=60)
    def scrap_metrics():
        provider_metric.scrap_metrics()

    scheduler.init_app(app)
    scheduler.start()

    return app
