from fastapi import FastAPI
from alert_generator import AlertGenerator
from google.cloud import pubsub_v1
from datetime import datetime

import os
import json
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    def __init__(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            os.environ["PROJECT_ID"], os.environ["TOPIC_NAME"]
        )


def get_future(message_data: bytes, config: Config = Config()):
    try:
        future = config.publisher.publish(config.topic_path, message_data)
        logger.info(f"Future OK: {str(future)}")
        return future

    except Exception as e:
        logger.error(f"Error publishing: {e}")
        raise e


@app.get("/generate")
def generate_alerts(count: int = 3):
    ag = AlertGenerator()
    try:
        res = ag.run(count)
        alerts = res["alerts"]
        for alert in alerts:
            message_data = json.dumps(
                {
                    "alert": alert,
                    "timestamp": datetime.now().isoformat(),
                }
            ).encode("utf-8")
            logger.debug(f"Successfully generated {count} alerts..")
            future = get_future(message_data)
            message_id = future.result(timeout=10)
            logger.info(f"Publishing {message_id} with success")
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


@app.get("/debug")
def debug_config():
    return {
        "PROJECT_ID": os.environ.get("PROJECT_ID"),
        "TOPIC_NAME": os.environ.get("TOPIC_NAME"),
        "topic_path": Config().topic_path,
        "key": os.environ.get("GOOGLE_API_KEY"),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
