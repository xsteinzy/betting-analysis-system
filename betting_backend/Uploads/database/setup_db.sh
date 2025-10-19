
#!/bin/bash

# NFL and NBA Betting Analysis Database Setup Script

echo "Setting up PostgreSQL database for Betting Analysis System..."

# Load environment variables if .env exists
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Default values
DB_NAME=${DB_NAME:-betting_analysis}
DB_USER=${DB_USER:-betting_user}
DB_PASSWORD=${DB_PASSWORD:-betting_password}

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
    echo "On Ubuntu/Debian: sudo systemctl start postgresql"
    echo "On macOS: brew services start postgresql"
    exit 1
fi

echo "PostgreSQL is running..."

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    read -p "Database '$DB_NAME' already exists. Drop and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping existing database..."
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
        sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;"
    else
        echo "Keeping existing database. Exiting..."
        exit 0
    fi
fi

# Create user and database
echo "Creating database user '$DB_USER'..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

echo "Creating database '$DB_NAME'..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# Run schema creation
echo "Creating tables and schema..."
PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -f schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Database setup completed successfully!"
    echo ""
    echo "Database Details:"
    echo "  Database: $DB_NAME"
    echo "  User: $DB_USER"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo ""
    echo "You can connect using:"
    echo "  psql -h localhost -U $DB_USER -d $DB_NAME"
else
    echo "✗ Error occurred during schema creation"
    exit 1
fi
