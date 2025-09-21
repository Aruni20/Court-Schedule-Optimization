import os
import time
import json
import random
from faker import Faker
from kafka import KafkaProducer
from datetime import datetime

# Environment variables
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKERS,
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
)
fake = Faker()

def generate_new_case_event():
    # Placeholder for a realistic case event structure
    return {
        "event_type": "new_case_filing",
        "timestamp": datetime.now().isoformat(),
        "case_data": {
            "case_id": str(fake.unique.uuid4()),
            "filing_date": fake.date_between(start_date="-2y", end_date="today").isoformat(),
            "is_urgent": random.choice([True, False]),
            "vulnerability_score": round(random.uniform(0, 1), 2),
            "estimated_duration_blocks": random.randint(1, 4)
        }
    }

def main():
    try:
        while True:
            event = generate_new_case_event()
            producer.send('court_events', value=event)
            print(f"Produced event: {event['event_type']} for case {event['case_data']['case_id']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Producer shutting down...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()