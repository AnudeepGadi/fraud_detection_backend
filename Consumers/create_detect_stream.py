from ksql import KSQLAPI


# List of Kafka brokers
kafka_brokers = ["http://localhost:9022"]

# Kafka bootstrap servers string
bootstrap_servers = ",".join(kafka_brokers)

# Connect to ksqlDB
ksql_server = "http://localhost:8088"
ksql_client = KSQLAPI(ksql_server)

# Create ksqlDB streams for the Kafka topics
stream_rf = "STREAM_RF_DETECTOR"
stream_dt = "STREAM_DT_DETECTOR"
stream_xg = "STREAM_XG_DETECTOR"
joined_stream = "JOINED_STREAM"
output_topic = "transaction-response"


# stream_names = ['JOINED_STREAM', 'STREAM_DT_DETECTOR', 'STREAM_RF_DETECTOR', 'STREAM_XG_DETECTOR']
# # Delete each stream
# for stream_name in stream_names:
#     drop_stream_query = f"DROP STREAM {stream_name};"
#     ksql_client.ksql(drop_stream_query)

# print("All streams deleted successfully.")


create_stream_rf_query = f"CREATE OR REPLACE STREAM {stream_rf} (ID STRING, PREDICTION INT) \
                        WITH (KAFKA_TOPIC='rf-detector-response', VALUE_FORMAT='JSON')"

create_stream_dt_query = f"CREATE OR REPLACE STREAM {stream_dt} (ID STRING, PREDICTION INT) \
                        WITH (KAFKA_TOPIC='dt-detector-response', VALUE_FORMAT='JSON')"

create_stream_xg_query = f"CREATE OR REPLACE STREAM {stream_xg} (ID STRING, PREDICTION INT) \
                        WITH (KAFKA_TOPIC='xg-detector-response', VALUE_FORMAT='JSON')"

ksql_client.ksql(create_stream_rf_query)
ksql_client.ksql(create_stream_dt_query)
ksql_client.ksql(create_stream_xg_query)

# Apply a join between the two streams
join_query = f"CREATE STREAM {joined_stream} \
              WITH (KAFKA_TOPIC='{output_topic}', VALUE_FORMAT='JSON') \
              AS \
              SELECT {stream_rf}.ID, {stream_rf}.PREDICTION, {stream_dt}.PREDICTION, {stream_xg}.PREDICTION \
              FROM {stream_rf} \
              INNER JOIN {stream_dt} WITHIN 5 MINUTES ON {stream_rf}.ID = {stream_dt}.ID \
              INNER JOIN {stream_xg} WITHIN 5 MINUTES ON {stream_rf}.ID = {stream_xg}.ID"


ksql_client.ksql(join_query)

#the above commands can be run on docker exec -it ksqldb-cli ksql http://ksqldb-server:8088