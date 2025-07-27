import json
import base64
import firebase_admin
from google.cloud.firestore import Client

import logging

from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirestoreManager:
    def __init__(
        self, database: str = "alerts-store", collection: str = "alerts_collection"
    ) -> None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
            logger.debug("firebase app not found. setting up")
        logger.debug("firebase app found")
        self._collection = collection
        self._database = database
        self._db = Client(database=self._database)

    def write(self, data: Dict[str, List[Dict[str, str]]]) -> List[str] | None:
        alerts_container = data["alerts"]
        alerts_list = alerts_container["alerts"]
        refs = []
        for alert in alerts_list:
            try:
                ref = self._db.collection(self._collection).document()
                print(f"processing alert: {alert['alert_id']}")
                ref.set(alert)
                print(f"added alert: {alert['alert_id']} with ref: {ref.id}")
                refs.append(ref.id)
            except Exception as e:
                print(f"error writing alert {alert['alert_id']}: {e}")
                return None
        return refs


def _decode_message(event) -> Dict[str, List[Dict[str, str]]] | None:
    try:
        logger.debug("decoding event data..")
        data = base64.b64decode(event["data"]).decode("utf-8")
        logger.debug(f"decoded message data: {data}")
        logger.debug(f"decoded data type: {type(data)}")

        alerts = json.loads(data)
        logger.debug(f"parsed JSON type: {type(alerts)}")
        logger.debug(f"parsed JSON content: {alerts}")

        return alerts
    except Exception as e:
        logger.error(f"error decoding data: {e}")
        return None


def process_alerts(event, context):
    fm = FirestoreManager()
    data = _decode_message(event)
    if data is None:
        logger.error("got empty decoded data")
    try:
        fm.write(data)  # pyright: ignore
        return {"status": "success"}
    except Exception as e:
        print(f"error in process_alerts: {e}")
        return {"status": "failed", "error": str(e)}
