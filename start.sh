#!/bin/bash
set -e
set -x
exec > /app/media/migration.log 2>&1

echo "Starting server initialization..."

# 1. Collectstatic using production settings
export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
python manage.py collectstatic --noinput

# 2. Check if the database needs migration from SQLite
# If PostgreSQL has 0 users, it means it's a fresh database!
echo "Running migrations for PostgreSQL..."
export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
python manage.py migrate --noinput

# Check if Postgres has users using psql to avoid Python stdout warnings
USER_COUNT=$(PGPASSWORD=journal_pass123 psql -h postgres -U journal_user -d journal_db -tAc "SELECT count(*) FROM auth_user;" 2>/dev/null || echo "0")

# Fallback to 0 if it's not a valid number (e.g., if table doesn't exist)
if ! [[ "$USER_COUNT" =~ ^[0-9]+$ ]]; then
    USER_COUNT="0"
fi

if [ "$USER_COUNT" -eq "0" ] && [ -f "/app/db.sqlite3" ]; then
    echo "================================================="
    echo "PostgreSQL is empty. Migrating data from SQLite..."
    echo "================================================="
    
    # Dumpdata from SQLite
    export DJANGO_SETTINGS_MODULE=oncoscience.settings.sqlite
    echo "Dumping SQLite data to /tmp/datadump.json..."
    python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e admin.logentry -e sessions.session --indent 4 > /tmp/datadump.json 2>> /app/media/migration.log
    
    if [ -s "/tmp/datadump.json" ]; then
        # Loaddata into PostgreSQL
        export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
        echo "Loading JSON into PostgreSQL..."
        python manage.py loaddata /tmp/datadump.json >> /app/media/migration.log 2>&1
        echo "Data migration complete!"
    else
        echo "SQLite dump failed or was empty."
    fi
else
    echo "PostgreSQL already has data (Users: $USER_COUNT). Skipping migration."
fi

# Ensure production settings are active for Gunicorn
export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 oncoscience.wsgi:application
