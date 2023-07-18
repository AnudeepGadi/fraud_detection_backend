CREATE KEYSPACE IF NOT EXISTS fotc_keyspace
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE fotc_keyspace;

CREATE KEYSPACE IF NOT EXISTS fotc_keyspace
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE fotc_keyspace;

CREATE TABLE IF NOT EXISTS transactions (
  id UUID PRIMARY KEY,
  timestamp TIMESTAMP,
  type TEXT,
  amount DECIMAL,
  sender_initial_balance DECIMAL,
  receiver_initial_balance DECIMAL,
  fraud_methods MAP<TEXT, INT>
);
