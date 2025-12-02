#!/bin/bash

MAX_RETRIES=5        # 0 = infinite
RETRY_INTERVAL=10     # seconds between retries

# Load Environment Variables file and make sure they are found
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    exit 1
fi

source .env

# Comment if they are not there or wrong
if [ -z "$DB_HOST" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "Error: Missing required environment variables in .env!"
    exit 1
fi

DB_PORT=${DB_PORT:-5432}
export PGPASSWORD="$DB_PASSWORD"

echo "-------------------------------------------"
echo "PostgreSQL Auto-Retry Connection Script"
echo "-------------------------------------------"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "-------------------------------------------"
echo ""

# --- Connection Loop ---
attempt=1
while true; do
    echo "[Attempt $attempt] Trying to connect to $DB_HOST:$DB_PORT ..."
    if psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" --set=sslmode=require -c '\q' 2>/dev/null; then
        echo "Launching psql"
        psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" --set=sslmode=require
        break
    else
        echo "Connection failed. Retrying in ${RETRY_INTERVAL} seconds..."
    fi

    if [ "$MAX_RETRIES" -ne 0 ] && [ "$attempt" -ge "$MAX_RETRIES" ]; then
        echo "Reached max retries"
        break
    fi

    attempt=$((attempt + 1))
    sleep "$RETRY_INTERVAL"
done

unset PGPASSWORD
