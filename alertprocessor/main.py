from google.cloud.pubsub_v1 import SubscriberClient
from google.cloud.pubsub_v1.subscriber.message import Message

import os
from dotenv import load_dotenv


load_dotenv()


def subscribe():
    subscriber = SubscriberClient()
    subscription_path = subscriber.subscription_path(
        os.environ["PROJECT_ID"], os.environ["SUBSCRIPTION"]
    )
    with subscriber:
        try:
            streaming_pull_future = subscriber.subscribe(
                subscription_path, callback=callback
            )
            streaming_pull_future.result()

        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            print("exiting..\n")


def callback(message: Message) -> None:
    print(message.data)
    message.ack()


if __name__ == "__main__":
    subscribe()
