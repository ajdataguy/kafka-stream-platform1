"""
Notification Consumer — The final stop in the order pipeline.

THIS FILE TEACHES YOU:
  - End-to-end event flow through multiple services
  - How the last consumer in a pipeline might trigger side effects
    (send emails, push notifications, update dashboards)

RUN IT:
  python src/consumers/notification_consumer.py

THE COMPLETE FLOW:
  order_producer.py
    -> [orders topic]
      -> order_processor.py
        -> [notifications topic]
          -> THIS FILE (you are here!)
"""

import json
import sys
from datetime import datetime

from kafka import KafkaConsumer

sys.path.insert(0, ".")
from src.config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_NOTIFICATIONS,
    GROUP_NOTIFICATION_CONSUMERS,
)


def create_consumer():
    """Create a consumer for the notifications topic."""
    return KafkaConsumer(
        TOPIC_NOTIFICATIONS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_NOTIFICATION_CONSUMERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )


def send_notification(notification):
    """
    Simulate sending a notification.

    In a real system, this would:
    - Send an email via SendGrid/SES
    - Push a mobile notification via Firebase
    - Send a Slack/Teams message
    - Update a CRM system

    For learning, we just print it nicely.
    """
    status_emoji = {
        "CONFIRMED": "[OK]",
        "BULK_ORDER": "[BULK]",
        "FLAGGED_FOR_REVIEW": "[REVIEW]",
    }

    emoji = status_emoji.get(notification["status"], "[?]")

    print(f"  {emoji} To: {notification['customer_email']}")
    print(f"       Order: {notification['order_id'][:8]}...")
    print(f"       Status: {notification['status']}")
    print(f"       Message: {notification['message']}")
    print(f"       Amount: ${notification['total_price']}")
    print()


def main():
    """Main loop — consume and dispatch notifications."""
    consumer = create_consumer()

    print("Notification Consumer started")
    print(f"  Listening on: {TOPIC_NOTIFICATIONS}")
    print(f"  Consumer group: {GROUP_NOTIFICATION_CONSUMERS}")
    print("\nWaiting for notifications... (Press Ctrl+C to stop)\n")

    notification_count = 0

    try:
        for message in consumer:
            notification = message.value
            notification_count += 1

            print(f"--- Notification #{notification_count} ---")
            send_notification(notification)

    except KeyboardInterrupt:
        print(f"\n\nStopping. Dispatched {notification_count} notifications.")
    finally:
        consumer.close()
        print("Notification Consumer shut down cleanly.")


if __name__ == "__main__":
    main()
