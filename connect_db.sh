#!/bin/bash

MAX_RETRIES=30        # 0 = infinite
RETRY_INTERVAL=10     # seconds between retries

# --- Load Environment Variables ---
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with variables:"
    echo "DB_HOST=your_host"
    echo "DB_PORT=5432"
    echo "DB_NAME=your_database"
    echo "DB_USER=your_username"
    echo "DB_PASSWORD=your_password"
    exit 1
fi

source .env

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
        echo "✅ Connection successful!"
        echo ""
        echo "Launching interactive psql shell..."
        echo ""
        # Drop into interactive shell
        psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" --set=sslmode=require
        break
    else
        echo "❌ Connection failed. Retrying in ${RETRY_INTERVAL}s..."
    fi

    if [ "$MAX_RETRIES" -ne 0 ] && [ "$attempt" -ge "$MAX_RETRIES" ]; then
        echo "❗ Reached max retries ($MAX_RETRIES). Exiting."
        break
    fi

    attempt=$((attempt + 1))
    sleep "$RETRY_INTERVAL"
done

unset PGPASSWORD
