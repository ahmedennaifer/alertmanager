from google.cloud.firestore import Client, FieldFilter

from datetime import datetime

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

    def _calculate_error_rate_percent(self) -> None:
        """error_count / total_requests * 100"""
        logger.debug("calculating error_rate_percent...")
        try:
            logger.debug("calculating total error count...")
            total_error_count = (
                self._db.collection(self._from_collection)  # pyright: ignore
                .sum(AlertField.ERROR_COUNT)
                .get()[0][0]
                .value
            )
            logger.info(
                f"total error count calculated with success: {total_error_count}"
            )

            logger.debug("calculating total requests...")
            total_requests = (
                self._db.collection(self._from_collection)  # pyright: ignore
                .sum(AlertField.TOTAL_REQUESTS)
                .get()[0][0]
                .value
            )
            logger.info(f"total requests calculated with success: {total_requests}")

            if total_requests > 0:
                res = round((total_error_count / total_requests) * 100, 2)
            else:
                res = 0.0

            logger.info(f"error_rate_percent: {res}")
            self._metrics[MetricField.ERROR_RATE_PERCENT] = res
            logger.info("metrics table updated with success")
        except Exception as e:
            logger.error(f"error calculating error_rate_percent: {e}")
            raise e

    def _calculate_average_resolution_time(self) -> None:
        """sum(resolution_minutes) / count(resolved_alerts)"""
        logger.debug("calculating average_resolution_time_min...")
        try:
            logger.debug("calculating total resolution time...")
            total_resolution_time = (
                self._db.collection(self._from_collection)  # pyright: ignore
                .sum(AlertField.RESOLUTION_MINUTES)
                .get()[0][0]
                .value
            )
            logger.info(
                f"total resolution time calculated with success: {total_resolution_time}"
            )

            logger.debug("calculating resolved alerts count...")
            resolved_alerts = (
                self._db.collection(self._from_collection)
                .where(
                    filter=FieldFilter(AlertField.STATUS, Operator.EQUAL, "resolved")
                )
                .count()
                .get()[0][0]
                .value
            )
            logger.info(f"resolved alerts calculated with success: {resolved_alerts}")

            if resolved_alerts > 0:
                res = round(total_resolution_time / resolved_alerts, 2)
            else:
                res = 0.0

            logger.info(f"average_resolution_time_min: {res}")
            self._metrics[MetricField.AVERAGE_RESOLUTION_TIME_MIN] = res
            logger.info("metrics table updated with success")
        except Exception as e:
            logger.error(f"error calculating average_resolution_time_min: {e}")
            raise e

    def _calculate_services_affected(self) -> None:
        """count unique services"""
        logger.debug("calculating services_affected...")
        try:
            docs = self._db.collection(self._from_collection).stream()
            unique_services = set()
            for doc in docs:
                service = doc.to_dict().get(AlertField.SERVICE)
                if service:
                    unique_services.add(service)
            services_count = len(unique_services)
            logger.info(f"services_affected: {services_count}")
            self._metrics[MetricField.SERVICES_AFFECTED] = services_count
            logger.info("metrics table updated with success")
        except Exception as e:
            logger.error(f"error calculating services_affected: {e}")
            raise e

    def _calculate_service_health_score(self) -> None:
        """(1 - critical_alerts/total_alerts) * 100"""
        logger.debug("calculating service_health_score...")
        try:
            logger.debug("calculating critical alerts count...")
            critical_alerts = (
                self._db.collection(self._from_collection)
                .where(
                    filter=FieldFilter(AlertField.SEVERITY, Operator.EQUAL, "critical")
                )
                .count()
                .get()[0][0]
                .value
            )
            logger.info(f"critical alerts calculated with success: {critical_alerts}")

            logger.debug("calculating total alerts count...")
            total_alerts = (
                self._db.collection(self._from_collection).count().get()[0][0].value  # pyright: ignore
            )
            logger.info(f"total alerts calculated with success: {total_alerts}")

            if total_alerts > 0:
                res = round((1 - (critical_alerts / total_alerts)) * 100, 2)
            else:
                res = 100.0

            logger.info(f"service_health_score: {res}")
            self._metrics[MetricField.SERVICE_HEALTH_SCORE] = res
            logger.info("metrics table updated with success")
        except Exception as e:
            logger.error(f"error calculating service_health_score: {e}")
            raise e

    def _calculate_metrics(self, limit: int = 5) -> None:
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
        # services affected
        self._calculate_services_affected()
        # average response time
        self._calculate_average_response_time()
        # error rate percent
        self._calculate_error_rate_percent()
        # average resolution time
        self._calculate_average_resolution_time()
        # service health score
        self._calculate_service_health_score()

    def write_to_db(self) -> None:
        logger.debug("writing to db initiated...")
        logger.debug("calculating metrics...")
        try:
            self._calculate_metrics()
            logger.info("calculated metrics with success")
        except Exception as e:
            logger.error(f"error calculating metrics: {e}")
            raise e

        timestamp = datetime.now()
        ref = self._db.collection(self._to_collection).document(
            document_id=str(timestamp)
        )
        try:
            ref.set(self._metrics)
            logger.info(f"successfully wrote metrics to collection. id : {ref.id}")
        except Exception as e:
            logger.error(f"error writing to db: {e}")
            raise e


def compute_metrics(event, context):
    logger.info("starting metrics calculation function...")
    try:
        r = FireStoreMetricsAggregator()
        r.write_to_db()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"error in compute_metrics: {e}")
        return {"status": "failed", "error": str(e)}
