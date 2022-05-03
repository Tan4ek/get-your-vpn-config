from datetime import datetime, timedelta
from typing import List

from repository.persistant import Persistent, TrafficRecordEntity
from repository.provider_metric import ProviderMetric


class ProvidersMetricService:

    def __init__(self, providers_metric: List[ProviderMetric], persistent: Persistent):
        self._providers_metric = providers_metric
        self._persistent = persistent

    def scrap_metrics(self):
        for provider_metric in self._providers_metric:
            try:
                provider_type = provider_metric.provider_type()
                print(f"scrap metrics for {provider_type}")
                last_date_from = self._persistent.last_date_traffic_record(provider_type)
                if not last_date_from:
                    last_date_from = datetime.utcnow() - timedelta(hours=1)
                data_usages = provider_metric.data_usage(last_date_from, datetime.utcnow())

                for data_usage in data_usages:
                    provider_entity = self._persistent.provider_by_external_id(data_usage.external_id)
                    if provider_entity:
                        traffic_entity = TrafficRecordEntity(id=0,
                                                             date_from=data_usage.date_from,
                                                             date_to=data_usage.date_to,
                                                             provider_id=provider_entity.id,
                                                             quantity_bytes=data_usage.data_usage_bytes)
                        self._persistent.save_traffic_record(traffic_entity)
                    else:
                        print(f"no provider for {data_usage.external_id}")
            except Exception as e:
                print(f"exception for provider {provider_metric}. {e}")
