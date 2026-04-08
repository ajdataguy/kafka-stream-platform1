# Kafka Stream Platform

A hands-on learning project for Apache Kafka on KRaft mode with Docker and Python.

## What This Project Does

- **Weather Data Pipeline** — Streams simulated sensor data through Kafka topics
- **Order Microservice** — Processes orders and triggers notifications via event-driven architecture
- **KRaft Mode** — Runs Kafka without ZooKeeper (the modern approach)
- **CI/CD Pipeline** — GitHub Actions for linting, testing, and Docker validation

## Quick Start

```bash
# 1. Start Kafka
cd docker && docker compose up -d

# 2. Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run the weather pipeline (two terminals)
python src/producers/weather_producer.py    # Terminal 1
python src/consumers/weather_consumer.py    # Terminal 2

# 4. Run the order pipeline (three terminals)
python src/consumers/order_processor.py     # Terminal 1
python src/consumers/notification_consumer.py  # Terminal 2
python src/producers/order_producer.py      # Terminal 3
```

## Project Structure

```
kafka-stream-platform/
├── .github/workflows/ci.yml    # CI/CD pipeline
├── docker/docker-compose.yml   # Kafka + UI on KRaft
├── src/
│   ├── config/settings.py      # Centralized configuration
│   ├── producers/
│   │   ├── weather_producer.py # Simulated IoT data stream
│   │   └── order_producer.py   # Simulated e-commerce orders
│   └── consumers/
│       ├── weather_consumer.py # Processes weather readings
│       ├── order_processor.py  # Processes orders → notifications
│       └── notification_consumer.py  # Dispatches notifications
├── tests/
│   ├── test_weather_producer.py
│   ├── test_order_processor.py
│   └── test_integration.py     # End-to-end Kafka test
├── LEARNING_GUIDE.md           # Step-by-step learning path
└── requirements.txt
```

## Kafka UI

After starting Docker, visit **http://localhost:8080** to visually explore topics, messages, and consumer groups.

## Running Tests

```bash
pytest tests/ -v                    # Unit tests
python tests/test_integration.py    # Integration test (requires Kafka)
```

## Learning Guide

See [LEARNING_GUIDE.md](LEARNING_GUIDE.md) for the complete step-by-step learning path.
