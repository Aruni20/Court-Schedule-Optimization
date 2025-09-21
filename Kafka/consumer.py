import os
import json
import random
import boto3
import pandas as pd
import mysql.connector
from kafka import KafkaConsumer
from datetime import datetime
from io import BytesIO

# Environment variables
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "court_db")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

consumer = KafkaConsumer(
    'court_events',
    bootstrap_servers=KAFKA_BROKERS,
    auto_offset_reset='earliest',
    group_id='event-processor-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def compute_priority(case_data):
    # This is where your real-time priority scoring logic would go
    return random.uniform(0.1, 1.0)

def main():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = conn.cursor()
        
        # Process events continuously
        for msg in consumer:
            event = msg.value
            if event['event_type'] == "new_case_filing":
                case_data = event['case_data']
                case_data['priority_score'] = compute_priority(case_data)
                
                insert_query = """
                INSERT INTO Case_Data (case_id, priority_score, is_urgent, filing_date)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE priority_score = VALUES(priority_score), is_urgent = VALUES(is_urgent)
                """
                cursor.execute(insert_query, (
                    case_data['case_id'],
                    case_data['priority_score'],
                    case_data['is_urgent'],
                    case_data['filing_date']
                ))
                conn.commit()
                print(f"Processed new case: {case_data['case_id']}")
                
    except KeyboardInterrupt:
        print("\nConsumer received termination signal. Uploading snapshot...")
        
        # Draining any remaining messages (optional but good practice)
        consumer.commit()
        
        # Pull all data from MySQL to create the final snapshot
        df = pd.read_sql("SELECT * FROM Case_Data", conn)
        
        # Upload the snapshot to MinIO
        s3 = boto3.client(
            's3',
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY
        )
        
        bucket_name = "court-data"
        try:
            s3.head_bucket(Bucket=bucket_name)
        except:
            s3.create_bucket(Bucket=bucket_name)
            
        file_name = f"cases_snapshot_{datetime.now().strftime('%Y%m%d')}.parquet"
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=parquet_buffer
        )
        
        print(f"Uploaded snapshot to MinIO as {file_name}")
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
        consumer.close()

if __name__ == "__main__":
    main()