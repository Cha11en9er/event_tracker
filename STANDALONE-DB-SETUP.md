# Standalone PostgreSQL Database Setup

This guide explains how to set up and configure a standalone PostgreSQL database for use with the Event Tracker application.

## Option 1: Using an Existing PostgreSQL Server

If you already have a PostgreSQL server running:

1. Create a new database for the application:
   ```sql
   CREATE DATABASE event_tracker_db;
   ```

2. Create a user with appropriate privileges:
   ```sql
   CREATE USER event_tracker_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE event_tracker_db TO event_tracker_user;
   ```

3. Configure your application's `.env` file with the correct connection information:
   ```
   DB_HOST=your_postgres_server_ip
   DB_PORT=5432
   DB_NAME=event_tracker_db
   DB_USER=event_tracker_user
   DB_PASSWORD=your_secure_password
   ```

## Option 2: Setting Up a New PostgreSQL Server

If you need to install PostgreSQL on a separate server:

### Ubuntu/Debian

```bash
# Update package lists
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Access PostgreSQL command line as postgres user
sudo -u postgres psql

# In PostgreSQL prompt, create database and user
postgres=# CREATE DATABASE event_tracker_db;
postgres=# CREATE USER event_tracker_user WITH PASSWORD 'your_secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE event_tracker_db TO event_tracker_user;
postgres=# \q

# Configure PostgreSQL to allow remote connections
sudo nano /etc/postgresql/*/main/postgresql.conf
# Uncomment and modify: listen_addresses = '*'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add this line to allow connections from your application server:
# host    all             all             your_app_server_ip/32         md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Configure Firewall

Don't forget to allow incoming connections to PostgreSQL:

```bash
sudo ufw allow 5432/tcp
```

## Testing the Connection

You can test the connection to your standalone database:

```bash
# Install the PostgreSQL client if needed
sudo apt install -y postgresql-client

# Test the connection
psql -h your_postgres_server_ip -U event_tracker_user -d event_tracker_db
```

If you can connect successfully, your application should be able to connect as well.

## Database Schema Setup

After deploying your application for the first time, you'll need to run your database schema migrations or setup scripts to create the necessary tables.

### Troubleshooting Connection Issues

If your application can't connect to the database:

1. Verify the database is running: `sudo systemctl status postgresql`
2. Check connection settings in your `.env` file
3. Ensure the PostgreSQL server is accepting remote connections
4. Check firewall rules on both the database server and application server
5. Verify the database user has appropriate privileges 