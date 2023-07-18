from joblib import load
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import json
from confluent_kafka import Consumer, Producer
import argparse
import sys

def min_max_scaler(transaction):
    types = {"CASH_IN": 0, "CASH_OUT": 0, "DEBIT": 0, "PAYMENT": 0, "TRANSFER": 0}
    types[transaction["type"]] = 1
    del transaction["type"]
    transaction = {**transaction, **types}

    df_transaction = pd.DataFrame([transaction]).to_numpy()
    scaler = MinMaxScaler()
    df_transaction = scaler.fit_transform(df_transaction)

    return df_transaction

def detect_fraud(model, data_dict):
    models = {
        "rf": r'models\rf.pkl',
        "dt": r'models\dt.pkl',
        "xg": r'models\xgb.pkl',
    }
    joblib_file_path = models.get(model, r'models\rf.pkl')
    decision_tree_model = load(joblib_file_path)

    data = min_max_scaler(data_dict)
    return decision_tree_model.predict(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Method Selection")
    parser.add_argument("-m", "--method", type=str, help="Specify the method to execute (rf, dt, xg)")

    args = parser.parse_args()

    # Check if the method argument is provided
    if not args.method:
        parser.print_help()
        sys.exit(1)

    # Get the method selection from the argument
    method_selection = args.method

    # Define the topic to consume from
    topic = 'transaction-request'

    # Create a Kafka Consumer instance
    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': f'{method_selection}-detector-group',
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(consumer_conf)

    # Subscribe to the topic
    consumer.subscribe([topic])

    # Create a Kafka Producer instance
    producer_conf = {
        'bootstrap.servers': 'localhost:9092'
    }
    producer = Producer(producer_conf)

    try:
        # Start consuming messages
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Decode the message value
            data = json.loads(msg.value().decode('utf-8'))

            id = data.pop("id")
            data.pop("connection_id")

            result = detect_fraud(method_selection, data)

            kafka_message = {"id": id, "prediction": int(result[0])}

            print(kafka_message)

            kafka_message = json.dumps(kafka_message).encode('utf-8')
            producer.produce(f'{method_selection}-detector-response', value=kafka_message)

    except KeyboardInterrupt:
        # Handle keyboard interruption (Ctrl+C)
        pass

    finally:
        # Close the Kafka Consumer and Producer
        consumer.close()
        producer.flush()
