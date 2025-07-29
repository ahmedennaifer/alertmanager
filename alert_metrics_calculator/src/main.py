from google.cloud.firestore import Client
from pprint import pprint
import firebase_admin

from typing import Any

import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# TODO: better read, more read features, etc..


class FSReader:
    def __init__(
        self, database: str = "alerts-store", collection: str = "alerts_collection"
    ) -> None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
            logger.debug("firebase app not found. setting up..")
        self._collection: str = collection
        self._database: str = database
        self._db: Client = self._get_client()

    def _get_client(self) -> Client:
        logger.debug("Setting up connection...")
        try:
            db = Client(database=self._database)
            logger.info("retrieved db with success")
            return db
        except Exception as e:
            logger.error(f"Error retrieving database: {e}")
            raise e

    def _read(self, limit: int = 5) -> Any:
        logger.debug(f"Trying to retrieve {limit} documents...")
        try:
            ref = self._db.collection(self._collection).limit(limit).stream()
            for doc in ref:
                data = doc.to_dict()
                pprint(data)
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise e


if __name__ == "__main__":
    r = FSReader()
    r._read()
