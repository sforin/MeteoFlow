#!/bin/sh
set -e

echo "⏳ Waiting for Kafka to be available at $KAFKA_BROKER..."
while ! nc -z ${KAFKA_BROKER%%:*} ${KAFKA_BROKER##*:}; do
  sleep 2
done

echo "✅ Kafka is up!"
exec "$@"
