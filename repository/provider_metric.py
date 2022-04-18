from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests


@dataclass
class ProviderTraffic:
    provider_type: str
    external_id: str
    data_usage_bytes: int
    date_from: datetime
    date_to: datetime


class ProviderMetricException(Exception):

    def __init__(self, message: str):
        self.message = message


class ProviderMetric:

    def data_usage(self, date_from: datetime, date_to: datetime) -> ProviderTraffic:
        pass


class PrometheusOpenvpnProviderMetric(ProviderMetric):

    def __init__(self, prom_url: str):
        self._prom_url = prom_url

    def data_usage(self, date_from: datetime, date_to: datetime) -> List[ProviderTraffic]:
        resp = requests.get(f"{self._prom_url}/api/v1/query?"
                            f"query=increase(openvpn_server_client_received_bytes_total"
                            f"[{(date_to - date_from).seconds}s])")
        if resp.status_code == 200:
            provider_traffics = []
            for result in resp.json()['data']['result']:
                common_name = result['metric']['common_name']
                data_usage_byte = int(float(result['value'][1]))
                provider_traffics.append(ProviderTraffic(
                    provider_type='openvpn',
                    external_id=common_name,
                    data_usage_bytes=data_usage_byte,
                    date_from=date_from,
                    date_to=date_to
                ))
            return provider_traffics
        else:
            raise ProviderMetricException(
                f"Can't get data usage. Status code: {resp.status_code}, response: {resp.text}")


if __name__ == '__main__':
    print(PrometheusOpenvpnProviderMetric('http://localhost:9092') \
          .data_usage(date_from=datetime.strptime('2022-04-18 18:00:00.243860', '%Y-%m-%d %H:%M:%S.%f'),
                      date_to=datetime.utcnow()))
