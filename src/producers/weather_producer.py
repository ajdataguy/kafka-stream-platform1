"""
Weather Data Producer — Simulates IoT sensor data streaming into Kafka.

THIS FILE TEACHES YOU:
  - How to create a KafkaProducer
  - How to serialize Python dicts to JSON
  - How to send messages to a Kafka topic
  - How to handle success/error callbacks
  - How to use partition keys for ordering

RUN IT:
  python src/producers/weather_producer.py

WHAT IT DOES:
  Every second, it generates a random weather reading for a city
  and publishes it to the "weather-data" topic.
"""

import json
import random
import time
import sys
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.errors import KafkaError

# Import our centralized settings
sys.path.insert(0, ".")
from src.config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_WEATHER_DATA,
    WEATHER_CITIES,
)


def create_producer():
    """
    Create and configure a Kafka producer.

    KEY CONCEPTS:
    - bootstrap_servers: Initial Kafka broker(s) to connect to.
      The producer discovers other brokers automatically.
    - value_serializer: Converts Python objects to bytes for Kafka.
      We use JSON here, but Avro/Protobuf are common in production.
    - key_serializer: Converts the message key to bytes.
      Keys determine which PARTITION a message goes to.
    - acks='all': Wait for ALL replicas to confirm. Safest option.
    - retries: Auto-retry on transient failures.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",  # Wait for all replicas (strongest guarantee)
        retries=3,  # Retry up to 3 times on failure
    )
    print(f"Producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
    return producer


def generate_weather_reading():
    """
    Generate a simulated weather reading.

    In a real system, this would come from an actual sensor/API.
    We add random variation to make the data interesting.
    """
    city_info = random.choice(WEATHER_CITIES)

    return {
        "city": city_info["city"],
        "state": city_info["state"],
        "temp_f": round(city_info["base_temp"] + random.uniform(-10, 10), 1),
        "humidity": min(100, max(0, city_info["base_humidity"] + random.randint(-15, 15))),
        "wind_mph": round(random.uniform(0, 30), 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def on_send_success(record_metadata):
    """Called when a message is successfully sent."""
    print(
        f"  -> Delivered to {record_metadata.topic} "
        f"[partition={record_metadata.partition}, offset={record_metadata.offset}]"
    )


def on_send_error(excp):
    """Called when a message fails to send."""
    print(f"  !! Error sending message: {excp}")


def main():
    """Main loop — continuously produce weather data."""
    producer = create_producer()
    message_count = 0

    print(f"\nProducing weather data to topic '{TOPIC_WEATHER_DATA}'...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # Generate a weather reading
            reading = generate_weather_reading()
            message_count += 1

            # Use the city name as the KEY.
            # WHY? Messages with the same key always go to the same partition.
            # This means all readings for "Austin" are ordered together.
            key = reading["city"]

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"#{message_count} Sending: {reading['city']} "
                f"{reading['temp_f']}°F, {reading['humidity']}% humidity"
            )

            # Send the message (asynchronous — returns a Future)
            future = producer.send(
                topic=TOPIC_WEATHER_DATA,
                key=key,
                value=reading,
            )

            # Add callbacks for success/failure
            future.add_callback(on_send_success)
            future.add_errback(on_send_error)

            # Wait 1 second between messages
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n\nStopping. Sent {message_count} messages total.")
    except KafkaError as e:
        print(f"\nKafka error: {e}")
        print("Is Kafka running? Try: docker compose up -d")
    finally:
        # IMPORTANT: Always flush and close the producer.
        # flush() ensures all buffered messages are sent.
        producer.flush()
        producer.close()
        print("Producer shut down cleanly.")


if __name__ == "__main__":
    main()
