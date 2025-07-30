from google.cloud.firestore import Client, FieldFilter
import firebase_admin

from enum import Enum

from typing import Dict

import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Operator(str, Enum):
    EQUAL = "=="
    LT = "<="
    BT = ">="


class AlertField(str, Enum):
    ALERT_ID = "alert_id"
    TIMESTAMP = "timestamp"
    SERVICE = "service"
    SEVERITY = "severity"
    STATUS = "status"
    RESPONSE_TIME_MS = "response_time_ms"
    ERROR_COUNT = "error_count"
    TOTAL_REQUESTS = "total_requests"
    RESOLUTION_MINUTES = "resolution_minutes"


class MetricField(str, Enum):
    TOTAL_ACTIVE_ALERTS = "total_active_alerts"
    CRITICAL_ALERTS = "critical_alerts"
    SERVICES_AFFECTED = "services_affected"
    AVERAGE_RESPONSE_TIME_MS = "average_response_time_ms"
    ERROR_RATE_PERCENT = "error_rate_percent"
    ALERTS_PER_HOUR = "alerts_per_hour"
    AVERAGE_RESOLUTION_TIME_MIN = "average_resolution_time_min"
    SERVICE_HEALTH_SCORE = "service_health_score"


METRICS = {
    "total_active_alerts": 0,
    "critical_alerts": 0,
    "services_affected": 0,
    "average_response_time_ms": 0.0,
    "error_rate_percent": 0.0,
    "alerts_per_hour": 0.0,
    "average_resolution_time_min": 0.0,
    "service_health_score": 0.0,
}


class FireStoreMetricsAggregator:
    def __init__(
        self,
        database: str = "alerts-store",
        from_collection: str = "alerts_collection",
        to_collection: str = "metrics",
        metrics: Dict[str, float] = METRICS,
    ) -> None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
            logger.debug("firebase app not found. setting up..")
        self._from_collection: str = from_collection
        self._to_collection: str = to_collection
        self._database: str = database
        self._db: Client = self._get_client()
        self._metrics: Dict[str, float] = metrics

    @property
    def metrics(self):
        return self._metrics

    def _get_client(self) -> Client:
        logger.debug("setting up connection...")
        try:
            db = Client(database=self._database)
            logger.info("retrieved db with success")
            return db
        except Exception as e:
            logger.error(f"error retrieving database: {e}")
            raise e

    def _calculate_single_metric(
        self, metric: MetricField, field: AlertField, operator: Operator, condition: str
    ) -> None:
        logger.debug(
            f"started calculation for metric {metric} with filters: {field + operator + condition}"
        )
        try:
            hits = (
                self._db.collection(self._from_collection)
                .where(filter=FieldFilter(field, operator, condition))
                .stream()
            )
            len_hits = len(list(hits))
            logger.info(f"found {len_hits} documents for {metric}..")
            self._metrics[metric] = len_hits
        except Exception as e:
            logger.error(
                f"error retrieving documents for metric {metric} with: {field + operator + condition}. Error {e} "
            )
            raise e

    def _calculate_average_response_time(self) -> None:
        """total response time / total alerts"""
        logger.debug("ealculating average_response_time_ms...")
        try:
            logger.debug("calculating the total reponse time..")
            total_response_time_ms = (
                self._db.collection(self._from_collection)  # pyright: ignore
                .sum(AlertField.RESPONSE_TIME_MS)
                .get()[0][0]
                .value
            )
            logger.info(
                f"total response time calculated with success: {total_response_time_ms}"
            )
            logger.debug("calculating total alerts..")
            total_alerts = (
                self._db.collection(self._from_collection).count().get()[0][0].value  # pyright: ignore
            )
            logger.info(f"total alerts calculated with success: {total_alerts}")
            res = round(total_response_time_ms / total_alerts, 2)
            logger.info(f"average_response_time_ms: {res}")
            self._metrics[MetricField.AVERAGE_RESPONSE_TIME_MS] = res
            logger.info("metrics table updated with success")
        except Exception as e:
            logger.error(f"error calculating average_response_time_ms: {e}")
            raise e

    def calculate_metrics(self, limit: int = 5) -> None:
        """
        Error Rate % = error_count / total_requests * 100
        Alerts Per Hour = count(alerts) / time_window_hours
        Average Resolution Time = sum(resolution_minutes) / count(resolved_alerts)
        Service Health Score = (1 - critical_alerts/total_alerts) * 100
        """
        logger.debug(f"trying to retrieve {limit} documents...")

        # total active alerts
        total_active_alerts_metric = MetricField.TOTAL_ACTIVE_ALERTS
        self._calculate_single_metric(
            metric=total_active_alerts_metric,
            field=AlertField.STATUS,
            operator=Operator.EQUAL,
            condition="active",
        )

        # critical alerts
        critical_alerts_metric = MetricField.CRITICAL_ALERTS
        self._calculate_single_metric(
            metric=critical_alerts_metric,
            field=AlertField.SEVERITY,
            operator=Operator.EQUAL,
            condition="critical",
        )
        # average response time
        self._calculate_average_response_time()


if __name__ == "__main__":
    r = FireStoreMetricsAggregator()
    r.calculate_metrics()
    print(r.metrics)
