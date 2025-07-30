import json
import base64
import firebase_admin
from google.cloud.firestore import Client

import logging

from typing import Dict, List

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FSWriter:
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
        logger.debug("starting to write data to db..")
        try:
            alerts_container = data["alerts"]["alerts"]  # pyright: ignore
        except Exception as e:
            logger.error(f"error trying to make container. got : {data}. Error: {e}")
            raise e
        try:
            alerts_list = alerts_container["alerts"]  # pyright: ignore
        except Exception as e:
            logger.error(
                f"error trying to make alerts_list. got: {alerts_container} Error: {e}"
            )
            raise e
        refs = []
        for alert in alerts_list:
            try:
                logger.debug(f"trying to insert alert: {alert['alert_id']}")
                ref = self._db.collection(self._collection).document(
                    document_id=alert["alert_id"]
                )
                ref.set(alert)
                logger.debug(f"added alert: {alert['alert_id']} with ref: {ref.id}")
                refs.append(ref.id)
            except Exception as e:
                logger.debug(f"error writing alert {alert['alert_id']}: {e}")
                raise e
        return refs


def _decode_message(event) -> Dict[str, List[Dict[str, str]]] | None:
    try:
        logger.debug("started message decoding")
        data = base64.b64decode(event["data"]).decode("utf-8")
        logger.info("decoded message with success")
        alerts = json.loads(data)
        return alerts
    except Exception as e:
        logger.error(f"error decoding data: {e}")
        return None


def process_alerts(event, context):
    fm = FSWriter()
    data = _decode_message(event)
    logger.info(f"got data: {data}")
    if data is None:
        logger.error("got empty decoded data")
        return {"status": "failed"}
    try:
        refs = fm.write(data)  # pyright: ignore
        return {"status": "success", "refs": refs}
    except Exception as e:
        logger.error(f"error in process_alerts: {e}")
        return {"status": "failed", "error": str(e)}
