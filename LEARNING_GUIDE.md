# Kafka Stream Platform — Hands-On Learning Guide

**Author:** Ajay's Learning Path  
**Stack:** Docker, Apache Kafka (KRaft), Python, GitHub Actions CI/CD  
**Level:** Beginner-friendly, project-based learning

---

## What You're Building

A **real-time event-driven data platform** that:

- Streams simulated weather/sensor data through Kafka topics (real-time pipeline)
- Processes orders and triggers notifications via Kafka consumers (event-driven microservice)
- Runs on Kafka in **KRaft mode** (no ZooKeeper — the modern way)
- Has CI/CD with GitHub Actions for linting, testing, and Docker validation

By the end, you'll understand Docker, Kafka internals, Python producers/consumers, and CI/CD pipelines.

---

## Prerequisites — Install These First

| Tool | What It Is | Install |
|------|-----------|---------|
| **Docker Desktop** | Runs containers on your machine | [docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Git** | Version control | [git-scm.com](https://git-scm.com/downloads) |
| **Python 3.10+** | Our application language | [python.org](https://www.python.org/downloads/) |
| **VS Code** | Code editor (recommended) | [code.visualstudio.com](https://code.visualstudio.com/) |
| **GitHub account** | For repo and CI/CD | [github.com](https://github.com/) |

---

## Phase 1: Git & GitHub Foundations

### Step 1.1 — Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `kafka-stream-platform`
3. Check "Add a README file"
4. Choose `.gitignore` template → **Python**
5. Choose License → **MIT**
6. Click **Create repository**

### Step 1.2 — Clone It Locally

Open your terminal and run:

```bash
git clone https://github.com/YOUR_USERNAME/kafka-stream-platform.git
cd kafka-stream-platform
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 1.3 — Understand the Git Workflow

Every time you complete a step in this guide, you'll commit your work:

```bash
git add .
git commit -m "feat: describe what you just did"
git push origin main
```

**Commit message conventions** (good habit to build early):

- `feat:` — new feature or file
- `fix:` — bug fix
- `docs:` — documentation changes
- `ci:` — CI/CD pipeline changes
- `refactor:` — code restructuring

### Checkpoint: Your First Commit

Copy the project files from this learning package into your cloned repo, then:

```bash
git add .
git commit -m "feat: initial project scaffolding"
git push origin main
```

---

## Phase 2: Docker Fundamentals

### Step 2.1 — Understand What Docker Does

Docker packages applications into **containers** — lightweight, portable units that include everything needed to run. Think of it like shipping containers for software: same box, runs the same everywhere.

**Key concepts:**

- **Image** — A blueprint/template (like a class in programming)
- **Container** — A running instance of an image (like an object)
- **Dockerfile** — Instructions to build an image
- **docker-compose.yml** — Defines multi-container applications
- **Volume** — Persistent storage that survives container restarts

### Step 2.2 — Verify Docker Is Running

```bash
docker --version
docker compose version
```

You should see version numbers for both. If not, make sure Docker Desktop is running.

### Step 2.3 — Your First Container

Try this to see Docker in action:

```bash
# Pull and run a simple container
docker run hello-world

# Run an interactive Ubuntu container
docker run -it ubuntu bash
# You're now INSIDE a container! Type 'exit' to leave.
```

### Step 2.4 — Read the docker-compose.yml

Open `docker/docker-compose.yml` in your editor. Here's what each section means:

```yaml
# Each "service" becomes a container
services:
  kafka:                          # Service name (you pick this)
    image: apache/kafka:3.9.0     # The image to use
    ports:
      - "9092:9092"               # host_port:container_port
    environment:                  # Configuration via env vars
      KAFKA_...: value
    volumes:
      - kafka_data:/var/lib/kafka # Persist data across restarts
```

### Step 2.5 — Launch Kafka

```bash
cd docker
docker compose up -d
```

The `-d` flag runs it in the background (detached mode). First run will download the Kafka image (~500MB), so be patient.

**Verify it's running:**

```bash
docker compose ps
docker compose logs kafka
```

You should see logs mentioning "Kafka Server started" and "KRaft" mode.

### Step 2.6 — Explore Container Commands

```bash
# See running containers
docker ps

# See logs in real-time
docker compose logs -f kafka

# Execute a command inside the container
docker compose exec kafka bash

# Stop everything
docker compose down

# Stop and DELETE all data
docker compose down -v
```

### Checkpoint: Commit

```bash
git add .
git commit -m "feat: add Docker Compose setup for Kafka KRaft"
git push origin main
```

---

## Phase 3: Kafka on KRaft — Deep Dive

### Step 3.1 — What Is KRaft?

**KRaft = Kafka Raft.** It's Kafka's built-in consensus protocol that replaces ZooKeeper.

- **Old way:** Kafka needed a separate ZooKeeper cluster to manage metadata
- **New way (KRaft):** Kafka manages its own metadata using the Raft consensus algorithm
- **Why it matters:** Simpler deployment, faster startup, fewer moving parts

In our `docker-compose.yml`, you'll see the KRaft configuration:

```
KAFKA_NODE_ID=1                             # Unique ID for this broker
KAFKA_PROCESS_ROLES=broker,controller       # This node does both roles
KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka:9093 # Who votes for the leader
```

### Step 3.2 — Kafka Core Concepts

| Concept | Explanation | Analogy |
|---------|------------|---------|
| **Broker** | A Kafka server that stores and serves data | A post office |
| **Topic** | A named stream of messages | A mailbox category |
| **Partition** | A topic is split into partitions for parallelism | Lanes in a highway |
| **Producer** | Sends messages to topics | Someone mailing a letter |
| **Consumer** | Reads messages from topics | Someone checking their mailbox |
| **Consumer Group** | Multiple consumers sharing the work | A team splitting mail |
| **Offset** | Position of a message in a partition | A page number |

### Step 3.3 — Create Topics Using the CLI

First, get into the Kafka container:

```bash
docker compose exec kafka bash
```

Now create topics:

```bash
# Create the weather data topic (3 partitions for parallelism)
kafka-topics.sh --create \
  --topic weather-data \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

# Create the orders topic
kafka-topics.sh --create \
  --topic orders \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

# Create the notifications topic
kafka-topics.sh --create \
  --topic notifications \
  --partitions 1 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

# List all topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe a topic in detail
kafka-topics.sh --describe --topic weather-data --bootstrap-server localhost:9092
```

Type `exit` to leave the container.

### Step 3.4 — Test with CLI Producer/Consumer

Open **two terminal windows** side by side.

**Terminal 1 — Start a consumer:**
```bash
docker compose exec kafka kafka-console-consumer.sh \
  --topic weather-data \
  --from-beginning \
  --bootstrap-server localhost:9092
```

**Terminal 2 — Start a producer:**
```bash
docker compose exec kafka kafka-console-producer.sh \
  --topic weather-data \
  --bootstrap-server localhost:9092
```

Now type messages in Terminal 2 and watch them appear in Terminal 1 in real-time!

```
{"city": "Austin", "temp_f": 95, "humidity": 45}
{"city": "Seattle", "temp_f": 62, "humidity": 78}
```

Press `Ctrl+C` in both terminals when done.

### Checkpoint: Commit

```bash
git add .
git commit -m "docs: add Kafka KRaft notes and topic creation"
git push origin main
```

---

## Phase 4: Python Producers & Consumers

### Step 4.1 — Set Up Python Environment

```bash
# From the project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 4.2 — Run the Weather Data Producer

The file `src/producers/weather_producer.py` generates simulated weather data and sends it to the `weather-data` topic.

**Make sure Kafka is running first**, then:

```bash
python src/producers/weather_producer.py
```

You'll see output like:

```
[2026-04-08 10:15:32] Sent to weather-data: {"city": "Austin", "temp_f": 94.2, ...}
[2026-04-08 10:15:33] Sent to weather-data: {"city": "Seattle", "temp_f": 61.8, ...}
```

Press `Ctrl+C` to stop.

**Study the code:** Open `weather_producer.py` and note:

- How `KafkaProducer` connects to the broker
- How `json.dumps` serializes data
- How `producer.send()` publishes to a topic
- The `on_send_success` and `on_send_error` callbacks

### Step 4.3 — Run the Weather Data Consumer

In a **new terminal** (keep the producer running):

```bash
source venv/bin/activate
python src/consumers/weather_consumer.py
```

You'll see it receiving and processing the weather data in real time.

**Study the code:** Note how:

- `KafkaConsumer` subscribes to a topic
- `group_id` enables load balancing across multiple consumers
- `auto_offset_reset='earliest'` reads from the beginning
- Messages are deserialized from JSON

### Step 4.4 — Run the Order Pipeline

This demonstrates the event-driven microservice pattern.

**Terminal 1 — Start the order processor:**
```bash
python src/consumers/order_processor.py
```

**Terminal 2 — Start the notification consumer:**
```bash
python src/consumers/notification_consumer.py
```

**Terminal 3 — Send some orders:**
```bash
python src/producers/order_producer.py
```

Watch the flow: Order Producer → `orders` topic → Order Processor → `notifications` topic → Notification Consumer.

### Step 4.5 — Experiment!

Try these exercises to deepen your understanding:

1. **Run two weather consumers** with the same `group_id` — watch partitions get distributed
2. **Change the number of partitions** and see how it affects consumer groups
3. **Kill a consumer** mid-stream and watch another pick up the work
4. **Modify the producer** to send different data (stock prices, log events, etc.)

### Checkpoint: Commit

```bash
git add .
git commit -m "feat: add Python producers and consumers"
git push origin main
```

---

## Phase 5: CI/CD with GitHub Actions

### Step 5.1 — What Is CI/CD?

- **CI (Continuous Integration)** — Automatically test and validate every code change
- **CD (Continuous Delivery)** — Automatically prepare code for deployment

GitHub Actions runs your CI/CD pipeline. It's defined in YAML files under `.github/workflows/`.

### Step 5.2 — Understand the Pipeline

Open `.github/workflows/ci.yml`. The pipeline has these stages:

1. **Lint** — Checks code style with `flake8` and `black`
2. **Test** — Runs unit tests with `pytest`
3. **Docker Validate** — Verifies the Docker Compose config is valid
4. **Integration Test** — Spins up Kafka in CI and runs a real produce/consume test

### Step 5.3 — Trigger Your First Pipeline

Push any change to GitHub:

```bash
echo "# CI/CD is active!" >> README.md
git add README.md
git commit -m "ci: trigger first pipeline run"
git push origin main
```

Then go to your GitHub repo → **Actions** tab. You'll see the pipeline running!

### Step 5.4 — Fix Failing Checks

If the pipeline fails (and it might — that's normal!), click the failed job to see logs. Common fixes:

- **Lint failures:** Run `black src/ tests/` locally to auto-format
- **Test failures:** Run `pytest tests/ -v` locally to debug
- **Docker issues:** Run `docker compose config` to validate

### Step 5.5 — Branch Protection (Optional but Recommended)

Go to your repo → Settings → Branches → Add rule:

- Branch name pattern: `main`
- Check "Require status checks to pass before merging"
- Select the CI checks

Now you can't merge broken code!

### Checkpoint: Commit

```bash
git add .
git commit -m "ci: add GitHub Actions CI/CD pipeline"
git push origin main
```

---

## Phase 6: Level Up — Next Steps

Once you're comfortable with the basics, try these:

### 6.1 — Add Schema Registry
Add Confluent Schema Registry to validate message formats with Avro/JSON Schema.

### 6.2 — Multi-Broker Cluster
Expand `docker-compose.yml` to 3 brokers with replication factor of 3.

### 6.3 — Kafka Connect
Add connectors to stream data to/from databases, S3, Elasticsearch.

### 6.4 — Monitoring
Add Prometheus + Grafana to monitor Kafka metrics.

### 6.5 — CD Pipeline
Add deployment stages — push Docker images to Docker Hub or AWS ECR.

---

## Quick Reference — Useful Commands

### Docker
```bash
docker compose up -d          # Start all services
docker compose down           # Stop all services
docker compose down -v        # Stop and delete data
docker compose ps             # List running containers
docker compose logs -f kafka  # Follow Kafka logs
docker compose exec kafka bash  # Shell into container
```

### Kafka CLI (inside container)
```bash
kafka-topics.sh --list --bootstrap-server localhost:9092
kafka-topics.sh --describe --topic TOPIC_NAME --bootstrap-server localhost:9092
kafka-console-producer.sh --topic TOPIC_NAME --bootstrap-server localhost:9092
kafka-console-consumer.sh --topic TOPIC_NAME --from-beginning --bootstrap-server localhost:9092
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092
kafka-consumer-groups.sh --describe --group GROUP_NAME --bootstrap-server localhost:9092
```

### Git
```bash
git status                    # See what's changed
git add .                     # Stage all changes
git commit -m "message"       # Commit
git push origin main          # Push to GitHub
git log --oneline -10         # See recent commits
git branch feature-name       # Create a branch
git checkout feature-name     # Switch to it
```

### Python
```bash
python -m venv venv           # Create virtual environment
source venv/bin/activate      # Activate it
pip install -r requirements.txt  # Install dependencies
pytest tests/ -v              # Run tests
black src/ tests/             # Auto-format code
flake8 src/ tests/            # Check code style
```

---

## Troubleshooting

**Kafka won't start?**
```bash
docker compose down -v  # Clean slate
docker compose up -d    # Try again
```

**Port 9092 already in use?**
```bash
lsof -i :9092  # Find what's using it
# Then kill the process or change the port in docker-compose.yml
```

**Python can't connect to Kafka?**
- Make sure Kafka is running: `docker compose ps`
- Make sure you're using `localhost:9092` (not `kafka:9092` — that's for inside Docker)

**Consumer not receiving messages?**
- Check the topic exists: `kafka-topics.sh --list ...`
- Try `--from-beginning` flag
- Make sure producer and consumer use the same topic name
