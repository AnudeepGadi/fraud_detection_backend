from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from confluent_kafka import Producer, Consumer
import uuid
import redis
import json
from threading import Event
from flask_kafka import FlaskKafka
from cassandra.cluster import Cluster
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Initialize Redis and Kafka
redis_client = redis.Redis(host='localhost', port=6379)
kafka_bootstrap_servers = 'localhost:9092'

# Create a KafkaProducer instance
producer_conf = {
    "bootstrap.servers": "localhost:9092",
    "client.id": "transaction-producer"
}
producer = Producer(producer_conf)

topic = 'transaction-response'
INTERRUPT_EVENT = Event()

bus = FlaskKafka(INTERRUPT_EVENT,
                 bootstrap_servers=",".join(["localhost:9092"]),
                 group_id="transaction-response-group",
                  auto_offset_reset='latest'
                 )


# Connect to the Cassandra cluster
cluster = Cluster(['localhost'], port=9042) 
session = cluster.connect('fotc_keyspace') 

# Define the table and column names
table_name = 'transactions'
columns = ['id', 'type', 'timestamp', 'amount', 'sender_initial_balance',
           'receiver_initial_balance', 'fraud_methods']

# Generate the INSERT query
query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in columns])})"

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    welcome_message = 'Connection Established'
    emit('message', {'content': welcome_message})

# Event handler for new client connections
@socketio.on('transaction-start')
def handle_transaction(data):
    # Generate a unique ID for the client connection
    id = str(uuid.uuid4())
    data["id"] = id
    data["connection_id"] = request.sid
    # Store the client details in Redis
    data = json.dumps(data).encode('utf-8')
    redis_client.set(id, data)
    producer.produce(topic='transaction-request', value=data)
    # Emit the client ID to the client
    welcome_message = 'Transaction Started'
    emit('message', {'content': welcome_message})


# Event handler for client disconnections
@socketio.on('disconnect')
def handle_disconnect():
    pass

@bus.handle(topic)
def prediction_consumer(msg):
    id = msg.key.decode('utf-8')
    prediction_data = json.loads(msg.value)
    lst = list(prediction_data.values())
    majority = max(lst, key=lst.count)
    redis_data = redis_client.get(id)
    if redis_data is None:
        return
    redis_data = json.loads(redis_data)
    connection_id = redis_data["connection_id"]
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f%z')
    insert_data = {
        'id': uuid.UUID(id),
        'type': redis_data["type"],
        'transaction_timestamp': current_timestamp,
        'transaction_amount': redis_data["amount"],
        'sender_initial_balance': redis_data["oldbalanceOrg"],
        'receiver_initial_balance': redis_data["oldbalanceDest"],
        'fraud_methods': prediction_data,
    }
    #redis_client.delete(id)
    # Execute the INSERT query with the data
    session.execute(query, tuple(insert_data.values()))
    try:
        print(connection_id,redis_data)
        socketio.emit('message', {'prediction': majority, 'prediction_methods': prediction_data}, to=str(connection_id))
        print("SocketIO emit successful")
    except Exception as e:
        print("SocketIO emit failed:", str(e))



if __name__ == '__main__':
    try:
        bus.run()
        socketio.run(app, debug=True)
    except Exception as err:
        print(err)
    finally:
        session.shutdown()
        cluster.shutdown()

#.venv\Scripts\Activate && python server.py