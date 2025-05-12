#!/bin/bash
set -e

# Function to wait for the database to be ready
wait_for_db() {
  echo "Waiting for database..."
  
  # Extract host and port from DATABASE_URL
  if [[ $DATABASE_URL == postgresql://* ]]; then
    # Extract host from the URL (assuming format postgresql://user:pass@host:port/db)
    DB_HOST=$(echo $DATABASE_URL | sed -e 's|^postgresql://[^@]*@\([^:/]*\).*|\1|')
    # Extract port, defaulting to 5432 if not specified
    DB_PORT=$(echo $DATABASE_URL | sed -n -e 's|^postgresql://[^@]*@[^:]*:\([0-9]*\).*|\1|p')
    DB_PORT=${DB_PORT:-5432}
    
    echo "Checking connection to database at $DB_HOST:$DB_PORT..."
    
    # Wait until we can connect to the database
    until nc -z -v -w30 $DB_HOST $DB_PORT; do
      echo "Database is unavailable - sleeping"
      sleep 2
    done
    
    echo "Database is up and running!"
  else
    echo "Invalid DATABASE_URL format. Skipping database check."
  fi
}

# Run database migrations
run_migrations() {
  echo "Running database migrations..."
  alembic upgrade head
  echo "Migrations completed!"
}

# Main entrypoint logic
case "$1" in
  migrate)
    wait_for_db
    run_migrations
    ;;
  start)
    wait_for_db
    run_migrations
    echo "Starting A2A LangGraph Agent..."
    exec python main.py
    ;;
  *)
    # If custom command is provided, execute it
    exec "$@"
    ;;
esac 