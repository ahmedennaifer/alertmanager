import json
import base64


def process_alerts(event, context):
    print(f"event data: {event}")
    message_data = base64.b64decode(event["data"]).decode("utf-8")
    print(f"message: {message_data}")
    alerts = json.loads(message_data)
    print(f"alerts: {alerts}")
    return {"status": "processed", "count": len(alerts)}
