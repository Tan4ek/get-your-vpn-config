from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

import requests


class ProviderTrafficDirection(Enum):
    IN = 1
    OUT = 2


@dataclass
class ProviderTraffic:
    provider_type: str
    external_id: str
    data_usage_bytes: int
    date_from: datetime
    date_to: datetime
    direction: ProviderTrafficDirection


class ProviderMetricException(Exception):

    def __init__(self, message: str):
        self.message = message


class ProviderMetric:

    def data_usage(self, date_from: datetime, date_to: datetime) -> List[ProviderTraffic]:
        pass

    def provider_type(self) -> str:
        pass


class PrometheusOpenvpnProviderMetric(ProviderMetric):

    def __init__(self, prom_url: str):
        self._prom_url = prom_url

    def data_usage(self, date_from: datetime, date_to: datetime) -> List[ProviderTraffic]:
        resp = requests.get(f"{self._prom_url}/api/v1/query?"
                            f"query=sum by (common_name) (delta(openvpn_server_client_received_bytes_total"
                            f"[{(date_to - date_from).seconds}s]))")
        if resp.status_code == 200:
            provider_traffics = []
            for result in resp.json()['data']['result']:
                common_name = result['metric']['common_name']
                data_usage_byte = int(float(result['value'][1]))
                if data_usage_byte > 0:
                    provider_traffics.append(ProviderTraffic(
                        provider_type=self.provider_type(),
                        external_id=common_name,
                        data_usage_bytes=data_usage_byte,
                        date_from=date_from,
                        date_to=date_to,
                        direction=ProviderTrafficDirection.IN
                    ))
            return provider_traffics
        else:
            raise ProviderMetricException(
                f"Can't get data usage. Status code: {resp.status_code}, response: {resp.text}")

    def provider_type(self) -> str:
        return 'openvpn'


class PrometheusShadowsocksProviderMetric(ProviderMetric):

    def __init__(self, prom_url: str):
        self._prom_url = prom_url

    def data_usage(self, date_from: datetime, date_to: datetime) -> List[ProviderTraffic]:
        resp = requests.get(f"{self._prom_url}/api/v1/query?"
                            'query=increase(shadowsocks_data_bytes{status="OK",dir="c<p"}'
                            f"[{(date_to - date_from).seconds}s])")
        if resp.status_code == 200:
            provider_traffics = []
            for result in resp.json()['data']['result']:
                common_name = result['metric']['access_key']
                data_usage_byte = int(float(result['value'][1]))
                if data_usage_byte > 0:
                    provider_traffics.append(ProviderTraffic(
                        provider_type=self.provider_type(),
                        external_id=common_name,
                        data_usage_bytes=data_usage_byte,
                        date_from=date_from,
                        date_to=date_to,
                        direction=ProviderTrafficDirection.IN
                    ))
            return provider_traffics
        else:
            raise ProviderMetricException(
                f"Can't get data usage. Status code: {resp.status_code}, response: {resp.text}")

    def provider_type(self) -> str:
        return 'shadow_socks'


if __name__ == '__main__':
    print(PrometheusShadowsocksProviderMetric('http://localhost:9092') \
          .data_usage(date_from=datetime.strptime('2022-04-18 18:00:00.243860', '%Y-%m-%d %H:%M:%S.%f'),
                      date_to=datetime.utcnow()))
