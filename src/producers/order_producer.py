"""
Order Producer — Simulates an e-commerce order stream.

THIS FILE TEACHES YOU:
  - Producing structured business events
  - Using UUIDs as message keys
  - Sending a burst of messages (vs continuous stream)

RUN IT:
  python src/producers/order_producer.py

WHAT IT DOES:
  Generates 10 random orders and sends them to the "orders" topic,
  then exits. This simulates a batch of incoming orders.
"""

import json
import random
import sys
import uuid
from datetime import datetime, timezone

from kafka import KafkaProducer

sys.path.insert(0, ".")
from src.config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_ORDERS,
    ORDER_PRODUCTS,
)


def create_producer():
    """Create a Kafka producer for order events."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
    )


def generate_order():
    """
    Generate a simulated order.

    Each order has:
    - A unique order_id (UUID) — used as the Kafka message key
    - A random product from our catalog
    - A random quantity
    - A customer email
    - A timestamp
    """
    product = random.choice(ORDER_PRODUCTS)
    quantity = random.randint(1, 5)

    return {
        "order_id": str(uuid.uuid4()),
        "customer_email": f"customer{random.randint(100, 999)}@example.com",
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "total_price": round(product["price"] * quantity, 2),
        "status": "CREATED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    """Send a batch of simulated orders to Kafka."""
    producer = create_producer()
    num_orders = 10

    print(f"Sending {num_orders} orders to topic '{TOPIC_ORDERS}'...\n")

    for i in range(num_orders):
        order = generate_order()

        # Use order_id as the key — ensures all events for an order
        # (created, paid, shipped) go to the same partition and stay ordered
        producer.send(
            topic=TOPIC_ORDERS,
            key=order["order_id"],
            value=order,
        )

        print(
            f"  Order #{i + 1}: {order['order_id'][:8]}... "
            f"| {order['product_name']} x{order['quantity']} "
            f"| ${order['total_price']}"
        )

    # Flush ensures all messages are actually sent before we exit
    producer.flush()
    producer.close()

    print(f"\nAll {num_orders} orders sent successfully!")


if __name__ == "__main__":
    main()
