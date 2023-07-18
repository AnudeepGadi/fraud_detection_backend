# Fraud Detection using machine learning on Kafka Streaming Architecture

## High-Level Architecture Diagram:
![fotc drawio](https://github.com/AnudeepGadi/fraud_detection_backend/assets/111954019/0ad04e43-1262-450c-b082-4ba062a92c22)


## Should have docker and Python 3.9 installed

The machine learning repo can be found on https://github.com/devin-cline/cs5540_project_fraud_detection

# Machine Learning Code Execution and Setup

Follow the steps below to run the machine learning codes and set up the required environment:

## Running Machine Learning Codes

Execute the machine learning codes provided. These codes will save the models in the `.pkl` (pickle) format.

## Moving Models to the Consumers/Models Directory

Move the generated models to the `consumers/models` directory. Ensure that the models are named as follows:

## Setting Up Kafka and Related Services

1. Open the terminal and navigate to the Kafka directory.
2. Run the command `docker-compose up --build -d` to start the necessary services, including Kafka, ZooKeeper, Kafka Manager, ksqlDB, and ksqlDB-cli.

## Creating a Kafka Cluster

1. Open your browser and access `localhost:9000`.
2. Using the Kafka Manager UI, create a cluster named "fotc" with the following configuration:
   - ZooKeeper host: [Enter the ZooKeeper host]
   - Leave the remaining fields at their default values.
   - Click on the "Create" button to create the cluster.

## Creating Kafka Topics

Using the Kafka Manager UI, create the following topics:
- `transaction-start`
- `transaction-response`
- `rf-detector-response`
- `dt-detector-response`
- `xg-detector-response`

Set the number of partitions to 1 since you are on a local machine. You can also specify a value higher than 1 if desired.

## Setting Up Cassandra and Redis

1. Open the terminal and navigate to the Cassandra directory.
2. Run the command `docker-compose up --build -d` to start Cassandra, Redis, and Redis Commander.

## Creating Cassandra Tables

Access the Cassandra container and run the following command: `cqlsh -f fotc_database_objects/create-table.cql`. This will create the `transaction` table in Cassandra.

## Setting Up Consumers

1. Open the terminal and navigate to the Consumers directory.
2. Run the command `pip install -r requirements.txt` to install the required dependencies.
3. Start the predictor consumers using the following commands:
```
python predictor.py -m dt
python predictor.py -m rf
python predictor.py -m xg
```


## Creating ksqlDB Streams

Run the command `python create_detect_stream.py` to create the necessary streams in ksqlDB.

## Starting the Flask Server

1. Open the terminal and navigate to the Servers directory.
2. Run the command `pip install -r requirements.txt` to install the required dependencies.
3. Start the Flask server by running the command `python server.py`.

Make sure to follow the instructions in the given sequence to successfully set up the environment and run the machine learning codes.
