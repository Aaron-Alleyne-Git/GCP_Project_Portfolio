# kubernetes/apps/event-processor/app.py
from google.cloud import pubsub_v1, bigquery
from concurrent.futures import TimeoutError
import json
import os

PROJECT_ID = os.getenv('PROJECT_ID')
SUBSCRIPTION_ID = os.getenv('SUBSCRIPTION_ID')
DATASET_ID = os.getenv('DATASET_ID')
TABLE_ID = os.getenv('TABLE_ID')

subscriber = pubsub_v1.SubscriberClient()
bq_client = bigquery.Client()

subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

def callback(message):
    try:
        event_data = json.loads(message.data.decode('utf-8'))
        
        # Process event
        processed_event = {
            'event_id': event_data['id'],
            'event_type': event_data['type'],
            'timestamp': event_data['timestamp'],
            'user_id': event_data['user_id'],
            'metadata': json.dumps(event_data.get('metadata', {}))
        }
        
        # Insert to BigQuery
        table_ref = bq_client.dataset(DATASET_ID).table(TABLE_ID)
        errors = bq_client.insert_rows_json(table_ref, [processed_event])
        
        if errors:
            print(f"Errors inserting rows: {errors}")
            message.nack()
        else:
            message.ack()
            
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}")

try:
    streaming_pull_future.result()
except TimeoutError:
    streaming_pull_future.cancel()
    streaming_pull_future.result()