#!/bin/bash

# Configuration
PGDATA="/data/data/com.termux/files/home/flexam/pg_test_data"
LOGFILE="/data/data/com.termux/files/home/flexam/pg_test_log"
PORT=5433
PG_CTL="/data/data/com.termux/files/usr/bin/pg_ctl"
CREATEDB="/data/data/com.termux/files/usr/bin/createdb"
DROPDB="/data/data/com.termux/files/usr/bin/dropdb"

case "$1" in
    start)
        echo "Starting PostgreSQL on port $PORT..."
        $PG_CTL -D "$PGDATA" -l "$LOGFILE" start -o "-p $PORT"
        echo "Creating test database..."
        $CREATEDB -p "$PORT" flexam_test
        ;;
    stop)
        echo "Stopping PostgreSQL..."
        $DROPDB -p "$PORT" flexam_test || true
        $PG_CTL -D "$PGDATA" stop
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
