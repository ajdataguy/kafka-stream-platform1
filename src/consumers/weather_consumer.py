"""
Weather Data Consumer — Reads and processes weather sensor data.

THIS FILE TEACHES YOU:
  - How to create a KafkaConsumer
  - How consumer groups work
  - What auto_offset_reset means
  - How to deserialize JSON messages
  - How to process messages in a loop

RUN IT:
  python src/consumers/weather_consumer.py

EXPERIMENT:
  1. Run this consumer in one terminal
  2. Run weather_producer.py in another terminal
  3. Watch data flow in real-time!
  4. Try running TWO consumers with the same group_id and see
     how Kafka distributes partitions between them.
"""

import json
import sys
from datetime import datetime

from kafka import KafkaConsumer

sys.path.insert(0, ".")
from src.config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_WEATHER_DATA,
    GROUP_WEATHER_CONSUMERS,
)


def create_consumer():
    """
    Create and configure a Kafka consumer.

    KEY CONCEPTS:
    - group_id: Consumers with the same group_id form a "consumer group".
      Kafka distributes partitions among group members automatically.
      If you run 3 consumers with the same group_id on a topic with
      3 partitions, each consumer gets exactly 1 partition.

    - auto_offset_reset='earliest': When this consumer group reads a
      topic for the FIRST TIME, start from the beginning.
      'latest' = only read NEW messages (skip history).

    - enable_auto_commit=True: Kafka automatically tracks which messages
      you've read. If you restart, it picks up where you left off.

    - value_deserializer: Converts bytes back to Python objects.
    """
    consumer = KafkaConsumer(
        TOPIC_WEATHER_DATA,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_WEATHER_CONSUMERS,
        auto_offset_reset="earliest",  # Read from beginning on first run
        enable_auto_commit=True,  # Automatically track read position
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )
    print(f"Consumer connected to {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Consumer group: {GROUP_WEATHER_CONSUMERS}")
    return consumer


def process_weather_reading(message):
    """
    Process a single weather reading.

    In a real system, you might:
    - Store it in a database
    - Check for extreme weather alerts
    - Update a real-time dashboard
    - Compute rolling averages
    """
    data = message.value
    key = message.key

    # Simple alert logic — flag extreme temperatures
    alert = ""
    if data["temp_f"] > 95:
        alert = " !! HIGH TEMP ALERT"
    elif data["temp_f"] < 32:
        alert = " !! FREEZE WARNING"

    print(
        f"  [{data['timestamp'][:19]}] "
        f"{data['city']}, {data['state']}: "
        f"{data['temp_f']}°F, {data['humidity']}% humidity, "
        f"wind {data['wind_mph']} mph"
        f"{alert}"
        f"  (partition={message.partition}, offset={message.offset})"
    )


def main():
    """Main consumer loop — continuously read and process weather data."""
    consumer = create_consumer()

    print(f"\nListening on topic '{TOPIC_WEATHER_DATA}'...")
    print("Press Ctrl+C to stop.\n")

    message_count = 0

    try:
        # This loop runs forever, polling Kafka for new messages.
        # When new messages arrive, they're yielded one at a time.
        for message in consumer:
            message_count += 1
            process_weather_reading(message)

    except KeyboardInterrupt:
        print(f"\n\nStopping. Processed {message_count} messages.")
    finally:
        # IMPORTANT: Always close the consumer cleanly.
        # This triggers a "rebalance" so other consumers in the group
        # can take over this consumer's partitions immediately.
        consumer.close()
        print("Consumer shut down cleanly.")


if __name__ == "__main__":
    main()
