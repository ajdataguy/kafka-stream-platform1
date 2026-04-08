"""
Order Processor — Consumes orders and produces notifications.

THIS FILE TEACHES YOU:
  - The "consume-process-produce" pattern
  - How one service can be BOTH a consumer AND a producer
  - Event-driven microservice architecture
  - Message transformation between topics

RUN IT:
  python src/consumers/order_processor.py

THE FLOW:
  order_producer.py -> [orders topic] -> THIS FILE -> [notifications topic] -> notification_consumer.py

This is a fundamental microservice pattern:
  1. Read an event from one topic
  2. Do some business logic (validate, transform, enrich)
  3. Publish a new event to another topic
"""

import json
import sys
from datetime import datetime, timezone

from kafka import KafkaConsumer, KafkaProducer

sys.path.insert(0, ".")
from src.config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_ORDERS,
    TOPIC_NOTIFICATIONS,
    GROUP_ORDER_PROCESSORS,
)


def create_consumer():
    """Create a consumer for the orders topic."""
    return KafkaConsumer(
        TOPIC_ORDERS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ORDER_PROCESSORS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )


def create_producer():
    """Create a producer for the notifications topic."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
    )


def process_order(order):
    """
    Simulate order processing business logic.

    In a real system, this might:
    - Validate the order
    - Check inventory
    - Process payment
    - Update the database

    Returns a notification event to be sent downstream.
    """
    # Simulate some validation logic
    if order["total_price"] > 500:
        status = "FLAGGED_FOR_REVIEW"
        message = f"High-value order ${order['total_price']} flagged for review"
    elif order["quantity"] > 3:
        status = "BULK_ORDER"
        message = f"Bulk order: {order['quantity']}x {order['product_name']}"
    else:
        status = "CONFIRMED"
        message = f"Order confirmed: {order['product_name']} x{order['quantity']}"

    # Create a notification event (this is the "transformation")
    notification = {
        "notification_id": f"NOTIF-{order['order_id'][:8]}",
        "order_id": order["order_id"],
        "customer_email": order["customer_email"],
        "type": "ORDER_UPDATE",
        "status": status,
        "message": message,
        "total_price": order["total_price"],
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    return notification


def main():
    """
    Main loop — consume orders, process them, produce notifications.

    This is the "consume-process-produce" pattern, one of the most
    common patterns in event-driven architectures.
    """
    consumer = create_consumer()
    producer = create_producer()

    print(f"Order Processor started")
    print(f"  Consuming from: {TOPIC_ORDERS}")
    print(f"  Producing to:   {TOPIC_NOTIFICATIONS}")
    print(f"  Consumer group: {GROUP_ORDER_PROCESSORS}")
    print("\nWaiting for orders... (Press Ctrl+C to stop)\n")

    order_count = 0

    try:
        for message in consumer:
            order = message.value
            order_count += 1

            print(f"--- Order #{order_count} received ---")
            print(
                f"  Order ID:  {order['order_id'][:8]}..."
                f"  Product:   {order['product_name']}"
                f"  Quantity:  {order['quantity']}"
                f"  Total:     ${order['total_price']}"
            )

            # Process the order and create a notification
            notification = process_order(order)

            # Publish the notification to the notifications topic
            producer.send(
                topic=TOPIC_NOTIFICATIONS,
                key=notification["order_id"],
                value=notification,
            )
            producer.flush()  # Ensure notification is sent immediately

            print(f"  -> Status: {notification['status']}")
            print(f"  -> Notification sent to '{TOPIC_NOTIFICATIONS}'\n")

    except KeyboardInterrupt:
        print(f"\n\nStopping. Processed {order_count} orders.")
    finally:
        consumer.close()
        producer.close()
        print("Order Processor shut down cleanly.")


if __name__ == "__main__":
    main()
