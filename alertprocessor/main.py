import json
import base64
import firebase_admin
from firebase_admin import firestore
from google.cloud import firestore as gcp_firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = gcp_firestore.Client(database="alerts-store")


def write():
    print("creating collection")
    try:
        ref = db.collection("alerts_collection").document()
        ref.set(
            {
                "alert": "test",
            }
        )
        print(f"created doc with id: {ref.id}")
        return ref.id
    except Exception as e:
        print("error creating collection or inserting doc: ", e)
        return None


def process_alerts(event, context):
    try:
        doc_id = write()
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        print(f"error in process_alerts: {e}")
        return {"status": "failed", "error": str(e)}
