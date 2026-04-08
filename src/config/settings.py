"""
Centralized configuration for the Kafka Stream Platform.

WHY THIS FILE EXISTS:
Instead of hardcoding values like "localhost:9092" in every file,
we define them once here. This makes it easy to change settings
and is a best practice for any project.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if it exists)
# This lets you override settings without changing code
load_dotenv()

# ---------------------------------------------------------------------------
# Kafka Connection
# ---------------------------------------------------------------------------
# Default: localhost:9092 (your local Docker Kafka)
# Override by setting KAFKA_BOOTSTRAP_SERVERS in your environment or .env file
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# ---------------------------------------------------------------------------
# Topic Names
# ---------------------------------------------------------------------------
# Defining these as constants prevents typos and makes renaming easy
TOPIC_WEATHER_DATA = "weather-data"
TOPIC_ORDERS = "orders"
TOPIC_NOTIFICATIONS = "notifications"

# ---------------------------------------------------------------------------
# Consumer Groups
# ---------------------------------------------------------------------------
# Consumer group IDs — consumers in the same group share the workload
# (each partition is assigned to exactly one consumer in the group)
GROUP_WEATHER_CONSUMERS = "weather-consumer-group"
GROUP_ORDER_PROCESSORS = "order-processor-group"
GROUP_NOTIFICATION_CONSUMERS = "notification-consumer-group"

# ---------------------------------------------------------------------------
# Producer Settings
# ---------------------------------------------------------------------------
# How many messages to batch before sending (higher = better throughput)
PRODUCER_BATCH_SIZE = 16384  # 16 KB

# Max time to wait before sending a batch (milliseconds)
PRODUCER_LINGER_MS = 10

# ---------------------------------------------------------------------------
# Simulated Data Settings
# ---------------------------------------------------------------------------
WEATHER_CITIES = [
    {"city": "Austin", "state": "TX", "base_temp": 85, "base_humidity": 55},
    {"city": "Seattle", "state": "WA", "base_temp": 58, "base_humidity": 75},
    {"city": "New York", "state": "NY", "base_temp": 65, "base_humidity": 60},
    {"city": "Miami", "state": "FL", "base_temp": 82, "base_humidity": 80},
    {"city": "Denver", "state": "CO", "base_temp": 55, "base_humidity": 35},
]

ORDER_PRODUCTS = [
    {"id": "PROD-001", "name": "Wireless Headphones", "price": 79.99},
    {"id": "PROD-002", "name": "USB-C Hub", "price": 49.99},
    {"id": "PROD-003", "name": "Mechanical Keyboard", "price": 129.99},
    {"id": "PROD-004", "name": "Webcam HD", "price": 69.99},
    {"id": "PROD-005", "name": "Monitor Stand", "price": 39.99},
]
