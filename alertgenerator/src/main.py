from fastapi import FastAPI
from alert_generator import AlertGenerator
from google.cloud import pubsub_v1
from datetime import datetime
from typing import Any

import os
import json
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self) -> None:
        self._publisher = pubsub_v1.PublisherClient()
        self._topic_path = self._publisher.topic_path(
            os.environ["PROJECT_ID"], os.environ["TOPIC_NAME"]
        )

    def publish(self, message_data: bytes) -> Any:
        try:
            future = self._publisher.publish(self._topic_path, message_data)
            logger.info(f"Published: {str(future)}")
            return future

        except Exception as e:
            logger.error(f"Error publishing: {e}")
            raise e


@app.get("/generate")
def generate_alerts(count: int):
    ag = AlertGenerator()
    pub = Publisher()
    try:
        logger.debug("started alert generation")
        alerts = ag.run(count)["alerts"]
        logger.info(f"generated {len(alerts)} alerts")
        for alert in alerts:
            message_data = json.dumps(
                {
                    "alert": alert,
                    "timestamp": datetime.now().isoformat(),
                }
            ).encode("utf-8")

            logger.debug(
                f"publishing started for message: {message_data.decode('utf-8')}"
            )
            future = pub.publish(message_data)
            message_id = future.result(timeout=10)
            logger.info(f"published message with id:{message_id} with success")

        return {
            "status": "success",
            "count": count,
            "result": alerts,
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "reason": f"{e}"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
