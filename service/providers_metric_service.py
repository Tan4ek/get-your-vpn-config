import logging
from datetime import datetime, timedelta
from typing import List

from repository.persistant import Persistent, TrafficRecordEntity, TrafficDirection
from repository.provider_metric import ProviderMetric, ProviderTrafficDirection

log = logging.getLogger(__name__)


def traffic_direction_converter(t: ProviderTrafficDirection) -> TrafficDirection:
    if t is ProviderTrafficDirection.IN:
        return TrafficDirection.IN
    elif t is ProviderTrafficDirection.OUT:
        return TrafficDirection.OUT
    else:
        raise ValueError(f"Invalid 'ProviderTrafficDirection' {t}")


class ProvidersMetricService:

    def __init__(self, providers_metric: List[ProviderMetric], persistent: Persistent):
        self._providers_metric = providers_metric
        self._persistent = persistent

    def scrap_metrics(self):
        for provider_metric in self._providers_metric:
            try:
                provider_type = provider_metric.provider_type()
                logging.info("Scrap metrics for %s", provider_type)
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
                                                             direction=traffic_direction_converter(
                                                                 data_usage.direction),
                                                             quantity_bytes=data_usage.data_usage_bytes)
                        self._persistent.save_traffic_record(traffic_entity)
                    else:
                        log.info("no provider for %s", data_usage.external_id)
            except Exception as e:
                log.error("Error while scrap metrics for provider %s. Error: %s", provider_metric.provider_type(), e)
